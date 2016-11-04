create table if not exists 
  vk_users (
    user_id numeric,
    name text
  );

create table if not exists
  vk_activity (
    user_id numeric,
    log_date date,
    state jsonb
  );

-- alter timezone on a database
alter role {{user-role}} set timezone = 'Europe/Moscow';
 
-- get current state by user
create or replace function current_state(
  i_user_id numeric,
  i_log_date date default current_date
) returns jsonb
as $$
  select state
  from vk_activity
  where user_id = i_user_id
    and log_date = i_log_date;
$$ language sql immutable;

-- get current state by name
create or replace function current_state(
  i_name text,
  i_log_date date default current_date
) returns jsonb
as $$
  select act.state
  from vk_activity act
    join vk_users usr
      on (usr.user_id = act.user_id)
  where usr.name = i_name
    and act.log_date = i_log_date;
$$ language sql immutable;
 
-- get the current minute (not used)
create or replace function current_minute(dt interval default '3 hours')
returns int
as $$
  select (extract(epoch from localtime + dt) / 60)::int;
$$ language sql immutable;
 
-- merge 2 JSON objects with SQL way
create or replace function json_merge(obj1 json, obj2 json)
returns json
as $$
  select json_object_agg(deduped.key, deduped.value)
  from (
      select distinct on (key) key, value
      from (
          select key, value, 1 as precedence from json_each(obj1) union all
          select key, value, 2 as precedence from json_each(obj2)
        ) as combined
      order by key, precedence desc
    ) as deduped;
$$ language sql immutable;
 
-- update user activity
create or replace function update_activity(
  i_user_id numeric,
  i_state json,
  i_log_date date default current_date
) returns void
as $$
  with upd as (
      update vk_activity
      set state = json_merge(state::json, i_state)::jsonb
      where user_id = i_user_id
        and log_date = i_log_date
      returning *
    )
  insert into vk_activity (user_id, log_date, state)
  select i_user_id, i_log_date, i_state::jsonb
  where not exists (select * from upd);
$$ language sql;
