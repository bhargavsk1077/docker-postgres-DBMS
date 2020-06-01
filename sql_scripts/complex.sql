--get all transactions type from a particular block
select tx_type from public.transaction where public.transaction.block_id=2;

--display posts from a particular user 
select * from public.post where public.post.author_id = 1;

--display all the messages/post in particular block
--messages
select body as message from public.message natural join public.transaction where public.transaction.message_id = public.message.message_id and public.transaction.block_id=1;

--posts
select content as post from public.post natural join public.transaction where public.transaction.post_id = public.post.post_id and public.transaction.block_id=1;

--display the list of all the followers of a particular user
select username from public.user natural join public.followers where public.user.user_id = public.followers.follower_id and public.followers.followed_id=1 ;

--display the count of ppl a particular user is following and count of number of followers
--followers
select count(follower_id) from public.followers where follower_id = 1;

--following
select count(followed_id) from public.followers where follower_id = 1;

--display the names of the users who have no followers
select username from public.user left outer join public.followers on public.user.user_id = public.followers.followed_id where public.followers.follower_id is null;

--display the names of the users who do not follow anyone
select username from public.user where not exists (select followed_id from public.followers where followers.follower_id = public.user.user_id);

--display the posts of followed users
select content from public.post where public.post.author_id in (select followed_id from public.followers where public.followers.follower_id = 2);

--display the conversation between two users
select username, body, msg_timestamp from public.user right outer join public.message on public.user.user_id = public.message.sender_id where public.message.sender_id in (1,2) and public.message.recipient_id in (1,2) order by public.message.msg_timestamp; 
 
--dislay the usernmae and followers of the user with the most number of followers
WITH fol_counts(username, fol_count) AS (select username , count(follower_id) as fol_count from public.user inner join public.followers on public.followers.followed_id = public.user.user_id group by public.user.username), max_fol(fol_count) AS (select MAX(fol_count) from fol_counts as follower_count) SELECT username,fol_count FROM user NATURAL JOIN fol_counts WHERE fol_count IN (SELECT fol_count FROM max_fol);

--search for users or post based on a pattern
select * from public.user where public.user.username like '%wa%';
