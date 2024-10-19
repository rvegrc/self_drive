

drop table tmp.messages;

CREATE TABLE tmp.messages
(
    message_id UInt32,
    sender_id UInt32,
    receiver_id UInt32,
    reply_message_id Nullable(UInt32)
)
ENGINE = MergeTree()
ORDER BY tuple();



show grants for developer  -- show grants for user;


grant developer to chdev; -- grant user to role;