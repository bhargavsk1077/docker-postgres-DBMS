--BLOCK

insert into public.block values 
(0,default,0,'0','123');

insert into public.block values
(1,default,0,'123','345');

insert into public.block values
(2,default,0,'345','567');

insert into public.block values
(3,default,0,'567','789');


--USER

insert into public.user values
('bayek','bayek@origins.com','acorigins','i am bayek of siwa',1);

insert into public.user values
('kassandra','kassandra@odessy.com','acodessy','this is sparta',2);

insert into public.user values
('jacob','jacob@syndicate.com','acsyndicate','lets fight',3);

insert into public.user values 
('edward','edward@ac4.com','jackdaw','im a pirate',4);

insert into public.user values
('connor','connor@ac3.com','whereischarleslee','i like forests',5);


--POST

insert into public.post values
(1,'first post',default,1);

insert into public.post values
(2,'sparta kick',default,2);

insert into public.post values
(3,'i like my hat',default,3);

insert into public.post values
(4,'you guys should visit athens',default,2);

--MESSAGE

insert into public.message values
(1,'yo whats up',default,3,2);

insert into public.message values
(2,'hey jacob',default,1,3);

insert into public.message values
(3,'hey bayek',default,2,1);

insert into public.message values
(4,'hello',default,1,2);

insert into public.message values
(5,'where are you from',default,2,1);

insert into public.message values
(6,'i am from egypt',default,1,2);


--FOLLOWERS

insert into public.followers values
(1,2);

insert into public.followers values
(2,1);

insert into public.followers values
(3,2);

insert into public.followers values
(1,3);

insert into public.followers values
(1,4);

insert into public.followers values
(5,4);

insert into public.followers values
(3,4);


--TRANSACTION

insert into public.transaction values
(1,'post',1,1,null);

insert into public.transaction values
(2,'post',1,2,null);

insert into public.transaction values
(3,'message',1,null,1);

insert into public.transaction values
(4,'message',1,null,2);

insert into public.transaction values
(5,'post',2,3,null);

insert into public.transaction values
(6,'message',2,null,3);

insert into public.transaction values
(7,'message',2,null,4);

insert into public.transaction values
(8,'post',3,4,null);

insert into public.transaction values
(9,'message',3,null,5);

insert into public.transaction values
(10,'message',3,null,6);


--PEERS

insert into public.peers values
(1,'191.168.0.1:8000');

insert into public.peers values
(2,'192.168.0.1:8001');


--LISTING ALL TABLES AFTER INSERTION

select * from public.block;
select * from public.user;
select * from public.post;
select * from public.message;
select * from public.followers;
select * from public.transaction;
select * from public.peers;






