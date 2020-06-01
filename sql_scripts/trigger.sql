CREATE EXTENSION IF NOT EXISTS pgcrypto;

drop trigger if exists set_hash on public.user;

create or replace function set_hash() returns trigger as 
$set_hash$
	begin
		new.password := crypt(new.password, gen_salt('md5'));
		return new;
	end;
$set_hash$ language plpgsql;


create trigger set_hash
before insert or update 
of password 
on public.user
for each row execute procedure set_hash();

	
