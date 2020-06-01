CREATE TABLE User
(
  username VARCHAR NOT NULL,
  email VARCHAR NOT NULL,
  password VARCHAR NOT NULL,
  about_me VARCHAR,
  user_id INT NOT NULL,
  PRIMARY KEY (user_id),
  UNIQUE (username),
  UNIQUE (email)
);

CREATE TABLE Post
(
  post_id INT NOT NULL,
  content VARCHAR NOT NULL,
  post_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  auhtor_id INT NOT NULL,
  PRIMARY KEY (post_id),
  FOREIGN KEY (auhtor_id) REFERENCES User(user_id)
);

CREATE TABLE Message
(
  message_id INT NOT NULL,
  body VARCHAR NOT NULL,
  msg_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  sender_id INT NOT NULL,
  recipient_id INT NOT NULL,
  PRIMARY KEY (message_id),
  FOREIGN KEY (sender_id) REFERENCES User(user_id),
  FOREIGN KEY (recipient_id) REFERENCES User(user_id)
);

CREATE TABLE Block
(
  block_id INT NOT NULL,
  block_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  nonce INT NOT NULL,
  previous_hash VARCHAR NOT NULL,
  block_hash VARCHAR NOT NULL,
  PRIMARY KEY (block_id)
);

CREATE TABLE Peers
(
  peer_id INT NOT NULL,
  url VARCHAR NOT NULL,
  PRIMARY KEY (peer_id)
);

CREATE TABLE followers
(
  follower_id INT NOT NULL,
  followed_id INT NOT NULL,
  PRIMARY KEY (follower_id, followed_id),
  FOREIGN KEY (follower_id) REFERENCES User(user_id),
  FOREIGN KEY (followed_id) REFERENCES User(user_id)
);

CREATE TABLE Transaction
(
  transaction_id INT NOT NULL,
  tx_type VARCHAR NOT NULL,
  block_id INT NOT NULL,
  post_id INT,
  message_id INT,
  PRIMARY KEY (transaction_id),
  FOREIGN KEY (block_id) REFERENCES Block(block_id),
  FOREIGN KEY (post_id) REFERENCES Post(post_id),
  FOREIGN KEY (message_id) REFERENCES Message(message_id)
);

