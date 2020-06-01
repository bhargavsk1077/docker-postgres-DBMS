
from hashlib import sha256
import json
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from SQLAlchemy.orm import backref
from hashlib import md5


db = SQLAlchemy()

followers = db.Table('followers',
        db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
        db.Column('followed_id',db.Integer,db.ForeignKey('user.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True , unique=True)
    email = db.Column(db.String(120), index=True , unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default = datetime.utcnow)

    followed = db.relationship(
            'User',secondary=followers,
            primaryjoin=(followers.c.follower_id == id),
            secondaryjoin=(followers.c.followed_id == id),
            backref=db.backref('followers',lazy='dynamic'),lazy='dynamic')

    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic')
    last_message_read_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash , password)

    def follow(self,user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self,user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self,user):
        return self.followed.filter(
                followers.c.followed_id == user.id).count()>0

    def followers_list(self):
        followers_l=User.query.join(
                followers,(followers.c.follower_id==User.id)).filter(
                        followers.c.followed_id==self.id)
        return followers_l

    def following_list(self):
        following_l=User.query.join(
                followers,(followers.c.followed_id==User.id)).filter(
                        followers.c.follower_id==self.id)
        return following_l

    def followed_posts(self):
        followed = Post.query.join(
                followers,(followers.c.followed_id == Post.user_id)).filter(
                        followers.c.follower_id == self.id)
        own=Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def unfollowed_posts(self):
        fol=self.following_list().all()
        unfollowed = Post.query.filter(~Post.user_id.in_(f.id for f in fol)).filter(Post.user_id != self.id)
        return unfollowed.order_by(Post.timestamp.desc())

    def delete_info(self):
        Post.query.filter(Post.user_id==self.id).delete()
        db.session.commit()

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

class Block(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    transactions = db.relationship('Transaction',backref='parent_block',lazy='dynamic')
    block_timestamp = db.Column(db.DateTime,default = datetime.utcnow)
    previous_hash = db.Column(db.String(64))
    nonce = db.Column(db.Integer,default=0)
    block_hash = db.Column(db.String(64))

    def __init__(self,id,previous_hash,timestamp=datetime.utcnow(),nonce=0):
        super().__init__(id=id,previous_hash=previous_hash,block_timestamp=timestamp,nonce=nonce)
        self.id = id
        self.block_timestamp=timestamp
        self.previous_hash=previous_hash
        self.nonce = nonce

    def __repr__(self):
        return "<block {}>".format(self.id)

    def compute_tx_dict(self,tx_id,tx_type):
        if tx_type == "post":
            post = Post.query.filter_by(tx_id = tx_id)
            t={'author':post.author.username,'author_id':post.user_id,'content':post.content}
            tsp=post.post_timestamp
            if isinstance(tsp,datetime):
                t['post_timestamp']=tsp.timestamp()
            return t
        elif tx_type == "message":
            msg = Message.query.filter_by(tx_id = tx_id)
            t ={'sender_id':msg.sender_id,'recipient_id':msg.recipient_id,'body':msg.body}
            tsp=msg.msg_timestamp
            if isinstance(tsp,datetime):
                t['msg_timestamp']=tsp.timestamp()
            return t 

    def compute_hash(self):
        dict1= self.__dict__
        keys = list(dict1.keys())
        dictionary=dict() 
        for key in keys:
            if key in ["id","transactions","previous_hash","nonce"]:
                dictionary[key] = dict1[key]

        transactions=[]
        txs=self.transactions.all()
        for tx in txs: 
            t=self.compute_tx_dict(tx.id,tx.tx_type)
            t['tx_type']=tx.tx_type
            transactions.append(t)
            
        dictionary['transactions']=transactions 
        
        ts=self.block_timestamp
        if isinstance(ts,datetime):
            dictionary['block_timestamp']=ts.timestamp()


        block_str = json.dumps(dictionary,sort_keys=True)
        return sha256(block_str.encode()).hexdigest()
    
    def set_hash(self,hash_str):
        self.block_hash=hash_str

    def add_tx(self,tx_list):
        for t in tx_list:
            if t['tx_type']=="post":
                tx = Transaction(block_id=self.id,tx_type=t['tx_type']) 
            elif t['tx_type']=="message":
                tx = Transaction(block_id=self.id , tx_type=t['tx_type'])
            db.session.add(tx)
            db.session.commit()
            tr = Transaction.query.get(tx.id)
            tr.add_txs(t)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tx_id = db.Column(db.Integer,db.ForeignKey('transaction.id'))
    parent_tx = db.relationship('Transaction',backref=backref('message',uselist=False))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    msg_timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    

    def __repr__(self):
        return '<Message {}>'.format(self.body)
    

class Transaction(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    block_id = db.Column(db.Integer,db.ForeignKey('block.id'))
    tx_type = db.Column(db.String(7))
     

    def __repr__(self):
        return "<tx {}>".format(self.tx_type)

    def add_txs(self,tx_list):

        if t['tx_type']=="post":
            author = t['author']
            content = t['content']
            author_id = t['auhtor_id']
            post_timestamp = datetime.fromtimestamp(t['post_timestamp'])
            post = Post(user_id = author_id, content = content , tx_id = self.id , post_timestamp = post_timestamp)
            db.session.add(post)
            db.session.commit()
        elif t['tx_type']=="message":
            sender_id = t['sender_id']
            recipient_id = t['recipient_id']
            body = t['body']
            msg_timestamp = datetime.fromtimestamp(t['post_timestamp'])
            msg = Message(sender_id = sender_id, recipient_id = recipient_id, body = body, tx_id=self.id ,msg_timestamp=msg_timestamp)
            db.session.add(msg)
            db.session.commit()

    def destroy_txs(self):
        Post.query.filter_by(tx_id=self.id).delete()
        db.session.commit()
        Message.query.filter_by(tx_id=self.id).delete()
        db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)

    tx_id = db.Column(db.Integer,db.ForeignKey('transaction.id'))
    parent_tx = db.relationship('Transaction',backref=backref('post',uselist=False))
    
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    #author = db.Column(db.String(64))
    content = db.Column(db.String(140))
    post_timestamp = db.Column(db.DateTime,default = datetime.utcnow)

    def __repr__(self):
        return "<post {}>".format(self.content)

class Peers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    address = db.Column(db.String(100))
    
    def __repr__(self):
        return "<address {}>".format(self.address)

class Blockchain:
    difficulty = 2

    def __init__(self):
        self.chain=self.return_chain() 
        self.unconfirmed_transactions=[]

    @staticmethod
    def return_chain():
        chain=[]
        block_list = Block.query.all()
        for block in block_list:
            transactions = []        
            txs = Transaction.query.filter_by(block_id=block.id).all()
            for tx in txs:
                if tx.tx_type == "post":
                    post = Post.query.filter_by(tx_id = tx.id) 
                    t={'author':post.author.username,'content':post.content,'author_id':post.user_id}
                    ts = post.post_timestamp
                    if isinstance(ts,datetime):
                        t['post_timestamp']=ts.timestamp()
                    t['tx_type']=tx.tx_type
                    transactions.append(t)
                elif tx.tx_type == "message":
                    msg = Message.query.filter_by(tx_id = tx.id)
                    t = {'sender_id':msg.sender_id.'recipient_id':msg.recipient_id,'body':msg.body}
                    ts = msg.msg_timestamp
                    if isinstance(ts,datetime):
                        t['msg_timestamp']=ts.timestamp()
                    t['tx_type']=tx.tx_type
                    transactions.append(t)
            b={"id":block.id,
                    "previous_hash":block.previous_hash, 
                    "nonce":block.nonce,
                    "block_hash":block.block_hash,
                    "transactions":transactions}
            bts = block.block_timestamp
            if isinstance(bts,datetime):
                b["block_timestamp"]=bts.timestamp()
            chain.append(b)
        return chain


    def create_genesis(self):
        dt = datetime.fromtimestamp(0)
        genesis = Block(0,"0",dt)
        db.session.add(genesis)
        db.session.commit()
        proof=self.proof_work(0)
        self.add_block(0,proof)

    def new_transaction(self,transaction):
        #the transactions need to be in the form {"tx_type:"message"/"post",post/message fields}
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            return False
        
        last_block = self.last_block
        new_block = Block(last_block["id"]+1,last_block["block_hash"])
        #===========================================
        db.session.add(new_block)
        db.session.commit()

        new_block=Block.query.get(last_block["id"]+1)
        new_block.add_tx(self.unconfirmed_transactions)
        #db.session.commit()
        #=========================================
        
        new_id = last_block["id"]+1
        proof=self.proof_work(new_id)
        
        self.add_block(new_id,proof)
        self.unconfirmed_transactions=[]
        return new_block.id




    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def proof_work(block_id):
        
        block = Block.query.get(block_id)
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0'*Blockchain.difficulty):
            block.nonce+=1
            computed_hash=block.compute_hash()
        db.session.commit()
        return computed_hash

    def add_block(self, block_id, proof):
        
        block = Block.query.get(block_id)
        
        if block_id==0:
            previous_hash="0"
        else:    
            previous_hash = self.last_block["block_hash"]

        if previous_hash != block.previous_hash:
            #print("hash did not match")
            #print(previous_hash)
            #print(block.previous_hash)
            Transaction.query.filter_by(block_id=block.id).destroy_txs()
            Transaction.query.filter_by(block_id=block.id).delete()
            Block.query.filter_by(id=block.id).delete() 
            db.session.commit()
            return False

        if not Blockchain.is_valid_proof(block_id, proof):
            #print("is valid proof failed")
            Transaction.query.filter_by(block_id=block.id).destroy_txs()
            Transaction.query.filter_by(block_id=block.id).delete()
            Block.query.filter_by(id=block.id).delete()
            db.session.commit()
            return False

        block.set_hash(proof)
        db.session.commit()
        self.chain=self.return_chain()
        return True

    @classmethod
    def is_valid_proof(self, block_id, block_hash):
        
        block = Block.query.get(block_id)
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def is_valid(self,block,block_hash):
        #print(block)
        x= (block_hash.startswith('0'*Blockchain.difficulty) and
                block_hash == self.check_hash(block))
        print("inside is valid {}".format(x))
        return x


    @classmethod
    def check_chain_validity(self,chain):
        result = True
        previous_hash= "0"

        for block in chain:
            block_hash = block["block_hash"]
            del block["block_hash"] 
            if not self.is_valid(block,block_hash) or \
                    previous_hash != block["previous_hash"]:
                        result=False
                        break
            block["block_hash"],previous_hash = block_hash,block_hash
        #print("check chain vaildity result is {}".format(result))
        return result
    
    @staticmethod
    def create_instance(block):
        new_block=dict() 
        keys = list(block.keys())
        for key in keys:
            if key in ["id","transactions","block_timestamp","previous_hash","nonce"]:
                new_block[key]=block[key]

        return new_block

    @staticmethod
    def check_hash(block):
        
        block_str=json.dumps(block,sort_keys=True)
        return sha256(block_str.encode()).hexdigest()

