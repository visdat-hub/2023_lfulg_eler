--CREATE SCHEMA eler AUTHORIZATION visdat;GRANT ALL ON SCHEMA edit TO visdat;GRANT ALL ON SCHEMA edit TO arbeitsgruppe;GRANT ALL ON SCHEMA edit TO stb_user;


drop table if exists tmp1;
create temp table tmp1 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26
and (de = 'DESN_542688' or de = 'DESN_537368' or de = 'DESN_537192'
or description_text like '%Bahre%'
or description_text like '%Mehltheuer%'
or description_text like '%Döbitzbach%'
or description_text like '%Wildenfelser%'
);

------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse_roh;
create table eler.fluesse_roh as 
select a.*, st_intersection(a.geom, b.the_geom) as the_geom from eler.fluesse_31468 a inner join tmp1 b on a.geom && b.the_geom where st_intersects(a.geom,b.the_geom);

ALTER TABLE eler.fluesse_roh DROP COLUMN geom;

drop table if exists eler.fluesse_rohr;
create table eler.fluesse_rohr as 
select * from eler.fluesse_roh where rohr > 0;

drop table if exists eler.fluesse;
create table eler.fluesse as 
select * from eler.fluesse_roh where id not in (select id from eler.fluesse_rohr);

drop table if exists eler.fluesse_rohr;

------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse_buffer10_roh;
create table eler.fluesse_buffer10_roh as 
select *, st_buffer(the_geom,10) as geom from eler.fluesse;

ALTER TABLE eler.fluesse_buffer10_roh DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer10_roh RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer10_union;
create table eler.fluesse_buffer10_union as 
select st_union(the_geom) as the_geom from eler.fluesse_buffer10_roh;

--drop table if exists eler.fluesse_buffer10;
--create table eler.fluesse_buffer10 as 
--select ST_MakePolygon(the_geom) as the_geom from eler.fluesse_buffer10_line


drop table if exists eler.fluesse_buffer10_ohne_sied;
create table eler.fluesse_buffer10_ohne_sied as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer10_union a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 <> 7;

ALTER TABLE eler.fluesse_buffer10_ohne_sied DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer10_ohne_sied RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer10_acker;
create table eler.fluesse_buffer10_acker as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer10_union a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 = 1;

ALTER TABLE eler.fluesse_buffer10_acker DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer10_acker RENAME geom TO the_geom;


drop table if exists eler.fluesse_buffer10_ohne_sied_owk;
create table eler.fluesse_buffer10_ohne_sied_owk as 
select idarea_data, area_data, description_text, st_union(a.the_geom) as the_geom, st_area(st_union(a.the_geom))::numeric as area from eler.fluesse_buffer10_ohne_sied a inner join tmp1 b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom)
group by idarea_data, area_data, description_text;


drop table if exists eler.fluesse_buffer10_acker_owk;
create table eler.fluesse_buffer10_acker_owk as 
select idarea_data, area_data, description_text, st_union(a.the_geom) as the_geom, st_area(st_union(a.the_geom))::numeric as area from eler.fluesse_buffer10_acker a inner join tmp1 b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom)
group by idarea_data, area_data, description_text;

------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse_buffer25_roh;
create table eler.fluesse_buffer25_roh as 
select *, st_buffer(the_geom,25) as geom from eler.fluesse;

ALTER TABLE eler.fluesse_buffer25_roh DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer25_roh RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer25_union;
create table eler.fluesse_buffer25_union as 
select st_union(the_geom) as the_geom from eler.fluesse_buffer25_roh;

--drop table if exists eler.fluesse_buffer25;
--create table eler.fluesse_buffer25 as 
--select ST_MakePolygon(the_geom) as the_geom from eler.fluesse_buffer25_line


drop table if exists eler.fluesse_buffer25_ohne_sied;
create table eler.fluesse_buffer25_ohne_sied as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer25_union a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 <> 7;

ALTER TABLE eler.fluesse_buffer25_ohne_sied DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer25_ohne_sied RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer25_acker;
create table eler.fluesse_buffer25_acker as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer25_union a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 = 1;

ALTER TABLE eler.fluesse_buffer25_acker DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer25_acker RENAME geom TO the_geom;


drop table if exists eler.fluesse_buffer25_ohne_sied_owk;
create table eler.fluesse_buffer25_ohne_sied_owk as 
select idarea_data, area_data, description_text, st_union(a.the_geom) as the_geom, st_area(st_union(a.the_geom))::numeric as area from eler.fluesse_buffer25_ohne_sied a inner join tmp1 b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom)
group by idarea_data, area_data, description_text;


drop table if exists eler.fluesse_buffer25_acker_owk;
create table eler.fluesse_buffer25_acker_owk as 
select idarea_data, area_data, description_text, st_union(a.the_geom) as the_geom, st_area(st_union(a.the_geom))::numeric as area from eler.fluesse_buffer25_acker a inner join tmp1 b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom)
group by idarea_data, area_data, description_text;

------------------------------------------------------------------------------------------------------------------------------------------------------------

-- export nach  ../stb_sachsen/original/parameters/eler/owk_eler_gruen.shp

drop table if exists eler.import_sc_param_grs;
create table eler.import_sc_param_grs as
select a.idarea_data, a.area_data, a.description_text, round(a.area)/10000 as f10_ha, round(b.area)/10000 as f25_ha, round(c.area)/10000 as af10_ha, round(d.area)/10000 as af25_ha, 
round(c.area/a.area,3) as af10_durch_a10, round(d.area/b.area,3) as af25_durch_a25, 100.0-(round((c.area/a.area)/(d.area/b.area),3)*100.0) as fl_ist, 50.0 as fl_50, 100.0 as fl_100, 14.0 as fl_2018, f.the_geom
from  eler.fluesse_buffer10_ohne_sied_owk a 
inner join eler.fluesse_buffer25_ohne_sied_owk b on a.idarea_data = b.idarea_data
inner join eler.fluesse_buffer10_acker_owk c on a.idarea_data = c.idarea_data
inner join eler.fluesse_buffer25_acker_owk d on a.idarea_data = d.idarea_data
inner join spatial.area_data e on a. idarea_data = e.idarea_data 
inner join spatial.area_geom f on a.idarea_data = f.idarea_data where idarea = 26

------------------------------------------------------------------------------------------------------------------------------------------------------------

/*
drop table if exists eler.fluesse_buffer25_minus_10;
create table eler.fluesse_buffer25_minus_10 as 
select ST_Difference(b.the_geom, a.the_geom) as the_geom from eler.fluesse_buffer10_union a, eler.fluesse_buffer25_union b;

drop table if exists eler.fluesse_buffer25_minus_10_dump;
create table eler.fluesse_buffer25_minus_10_dump as 
select (ST_Dump(the_geom)).geom AS the_geom from eler.fluesse_buffer25_minus_10;


CREATE INDEX landuse_index_geom ON eler.landnutzung USING gist (the_geom);
CREATE INDEX fluesse_buffer10_union_index_geom ON eler.landnutzung USING gist (the_geom);
CREATE INDEX fluesse_buffer25_minus_10_index_geom ON eler.landnutzung USING gist (the_geom);

drop table if exists eler.fluesse_buffer25_minus_10_ln;
create table eler.fluesse_buffer25_minus_10_ln as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer25_minus_10 a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 <> 7;

ALTER TABLE eler.fluesse_buffer25_minus_10_ln DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer25_minus_10_ln RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer10_ln;
create table eler.fluesse_buffer10_ln as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer10_union a inner join eler.landnutzung b on a.the_geom && b.the_geom where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 <> 7;

ALTER TABLE eler.fluesse_buffer10_ln DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer10_ln RENAME geom TO the_geom;


drop table if exists eler.fluesse_buffer25_minus_10_ln_1;
create table eler.fluesse_buffer25_minus_10_ln_1 as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer25_minus_10 a inner join eler.landnutzung b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 = 1;

ALTER TABLE eler.fluesse_buffer25_minus_10_ln DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer25_minus_10_ln RENAME geom TO the_geom;

drop table if exists eler.fluesse_buffer10_ln_1;
create table eler.fluesse_buffer10_ln_1 as 
select a.*, st_intersection(a.the_geom, b.the_geom) as geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse_buffer10_union a inner join eler.landnutzung b on a.the_geom && b.the_geom 
where st_intersects(a.the_geom,b.the_geom) and idhn_st_1 = 1;

ALTER TABLE eler.fluesse_buffer10_ln_1 DROP COLUMN the_geom;
ALTER TABLE eler.fluesse_buffer10_ln_1 RENAME geom TO the_geom;
*/




