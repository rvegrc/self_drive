

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


create DATABASE if not exists ycup COMMENT 'database for yandex cup';

GRANT select ON ycup.* TO developer; -- rewrite errors

SHOW GRANTS FOR developer;

drop table if exists ycup.control;
    
CREATE TABLE ycup.control (
    id UInt32 COMMENT 'id поездки'
    ,`stamp_ns` UInt64 COMMENT 'время в наносекундах от начала сцены'
    ,`acceleration_level` Int16 COMMENT 'интенсивность ускорения, 0 - нет ускорения, + - ускорение, - - торможение'
    ,`steering` Float32 COMMENT 'угол поворота руля в градусах относительно центрального положения'
    ) 
    ENGINE = MergeTree()
    ORDER BY tuple();



drop table if exists ycup.localization;
    
CREATE TABLE ycup.localization (
    id UInt32 COMMENT 'id поездки'
    ,`stamp_ns` UInt64 COMMENT 'время в наносекундах от начала сцены'
    ,`x` Float32 COMMENT 'координата x, на восток'
    ,`y` Float32 COMMENT 'координата y, на север'
    ,`z` Float32 COMMENT 'координата z, в небо'
    ,`roll` Float32 COMMENT 'угол крена в радианах'
    ,`pitch` Float32 COMMENT 'угол тангажа в радианах'
    ,`yaw` Float32 COMMENT 'угол рыскания в радианах, считается относительно оси x в направлении оси y'
    ) 
    ENGINE = MergeTree()
    ORDER BY tuple();



drop table if exists ycup.metadata;
    
CREATE TABLE ycup.metadata (
    id UInt32 COMMENT 'id поездки'
    ,`vehicle_id` UInt8 COMMENT 'идентификатор ТС'
    ,`vehicle_model` UInt8 COMMENT 'идентификатор модели ТС'
    ,`vehicle_model_modification` UInt8 COMMENT 'идентификатор модификации модели ТС'
    ,`location_reference_point_id` UInt8 COMMENT 'идентификатор точки отсчета координат'
    ,`front_tire` UInt8 COMMENT 'идентификатор передних шин'
    ,`rear_tire` UInt8 COMMENT 'идентификатор задних шин'
    ,`ride_year` UInt16 COMMENT 'год поездки'
    ,`ride_month` UInt8 COMMENT 'месяц поездки'
    ,`ride_day` UInt8 COMMENT 'день поездки'
    ) 
    ENGINE = MergeTree()
    ORDER BY tuple();





show grants for developer  -- show grants for user;


grant developer to chdev; -- grant user to role;