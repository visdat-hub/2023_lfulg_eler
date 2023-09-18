drop table if exists eler.fluesse2_bok;
create table eler.fluesse2_bok as select * from eler."BOK_Gesamt_Lines_13_owk";
CREATE INDEX fluesse2_bok_roh_index_geom ON eler.fluesse2_bok USING gist (the_geom);
CREATE INDEX fluesse2_index_geom ON eler.fluesse2 USING gist (the_geom);



/*drop table if exists eler.fluesse2_bok_simplify;
create table eler.fluesse2_bok_simplify as select id, ST_SimplifyPreserveTopology(the_geom, 0.9) as the_geom from eler.fluesse2_bok;
CREATE INDEX fluesse2_fluesse2_bok_simplify_index_geom ON eler.fluesse2_bok_simplify USING gist (the_geom);*/


drop table if exists eler.owk;
create table eler.owk as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26
and (de = 'DESN_542688' or de = 'DESN_537368' or de = 'DESN_537192'
or description_text like '%Bahre%'
or description_text like '%Mehltheuer%'
or description_text like '%Döbitzbach%'
or description_text like '%Wildenfelser%'
);
CREATE INDEX owk_index_geom ON eler.owk USING gist (the_geom);


drop table if exists eler.owk_DESN_542688;
create table eler.owk_DESN_542688 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_542688';

drop table if exists eler.owk_DESN_537368;
create table eler.owk_DESN_537368 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_537368';

drop table if exists eler.owk_DESN_537192;
create table eler.owk_DESN_537192 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_537192';

drop table if exists eler.owk_DESN_54138;
create table eler.owk_DESN_54138 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_54138';

drop table if exists eler.owk_DESN_537346;
create table eler.owk_DESN_537346 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_537346';

drop table if exists eler.owk_DESN_5666332;
create table eler.owk_DESN_5666332 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_5666332';

drop table if exists eler.owk_DESN_5371488;
create table eler.owk_DESN_5371488 as 
select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26 and de = 'DESN_5371488';

------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_line_roh;
create table eler.fluesse2_bok_line_roh as 
select row_number() over () AS id, (st_dump(the_geom)).geom as the_geom from eler.fluesse2_bok;

drop table if exists eler.fluesse2_bok_line;
create table eler.fluesse2_bok_line as 
select row_number() over () AS id, the_geom from eler.fluesse2_bok_line_roh;

DROP TABLE eler.fluesse2_bok_line_roh;
CREATE INDEX fluesse2_bok_line_index_geom ON eler.fluesse2_bok_line USING gist (the_geom);


---------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_line_100;
create table eler.fluesse2_bok_line_100 as 
select id, ST_Segmentize(the_geom, 100) as the_geom from eler.fluesse2_bok_line; 

CREATE INDEX fluesse2_bok_line_100_index_geom ON eler.fluesse2_bok_line_100 USING gist (the_geom);



---------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_line_5;
create table eler.fluesse2_bok_line_5 as
SELECT row_number() over () AS id, id as id_old, i,
    ST_LineSubstring( the_geom, startfrac, LEAST( endfrac, 1 )) AS the_geom FROM (
SELECT id, the_geom, ST_Length(the_geom) len, 5 sublen FROM eler.fluesse2_bok_line
) AS d CROSS JOIN LATERAL (
SELECT i, (sublen * i) / len AS startfrac,
          (sublen * (i+1)) / len AS endfrac
FROM generate_series(0, floor( len / sublen )::integer ) AS t(i)
-- skip last i if line length is exact multiple of sublen
WHERE (sublen * i) / len <> 1.0
) AS d2; 


drop table if exists eler.fluesse2_bok_line_5_right;
create table eler.fluesse2_bok_line_5_right as 
select id, st_buffer(the_geom, 5, 'side=right') as the_geom from eler.fluesse2_bok_line_100; 

CREATE INDEX fluesse2_bok_line_5_right_index_geom ON eler.fluesse2_bok_line_5_right USING gist (the_geom);

drop table if exists eler.fluesse2_bok_line_5_left;
create table eler.fluesse2_bok_line_5_left as 
select id, st_buffer(the_geom, 5, 'side=left') as the_geom from eler.fluesse2_bok_line_100; 


-------------------------------------------------------------------------------------------------------------------------------

CREATE INDEX fluesse2_bok_line_5_left_index_geom ON eler.fluesse2_bok_line_5_left USING gist (the_geom);

drop table if exists eler.fluesse2_bok_line_5_right2;
create table eler.fluesse2_bok_line_5_right2 as 
select a.id, st_length(st_intersection(b.the_geom, a.the_geom)) as length, a.the_geom from eler.fluesse2_bok_line_5_right a inner join eler.fluesse2 b on b.the_geom && a.the_geom where st_intersects(b.the_geom, a.the_geom);

CREATE INDEX fluesse2_bok_line_5_right2_index_geom ON eler.fluesse2_bok_line_5_right2 USING gist (the_geom);


drop table if exists eler.fluesse2_bok_line_5_right3;
create table eler.fluesse2_bok_line_5_right3 as 
select id, sum(length) as length, the_geom from eler.fluesse2_bok_line_5_right2 group by id, the_geom;

CREATE INDEX fluesse2_bok_line_5_right3_index_geom ON eler.fluesse2_bok_line_5_right3 USING gist (the_geom);


drop table if exists eler.fluesse2_bok_line_5_right4;
create table eler.fluesse2_bok_line_5_right4 as 
select id, length, the_geom from eler.fluesse2_bok_line_5_right3
union
select a.id, 0 as length, a.the_geom from eler.fluesse2_bok_line_5_right a full join eler.fluesse2_bok_line_5_right3 b on a.id = b.id where b.id is null order by id;

CREATE INDEX fluesse2_bok_line_5_right4_index_geom ON eler.fluesse2_bok_line_5_right4 USING gist (the_geom);


--------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_line_5_left2;
create table eler.fluesse2_bok_line_5_left2 as 
select a.id, st_length(st_intersection(b.the_geom, a.the_geom)) as length, a.the_geom from eler.fluesse2_bok_line_5_left a inner join eler.fluesse2 b on b.the_geom && a.the_geom where st_intersects(b.the_geom, a.the_geom);

CREATE INDEX fluesse2_bok_line_5_left2_index_geom ON eler.fluesse2_bok_line_5_left2 USING gist (the_geom);

drop table if exists eler.fluesse2_bok_line_5_left3;
create table eler.fluesse2_bok_line_5_left3 as 
select id, sum(length) as length, the_geom from eler.fluesse2_bok_line_5_left2 group by id, the_geom;

CREATE INDEX fluesse2_bok_line_5_left3_index_geom ON eler.fluesse2_bok_line_5_left3 USING gist (the_geom);

drop table if exists eler.fluesse2_bok_line_5_left4;
create table eler.fluesse2_bok_line_5_left4 as 
select id, length, the_geom from eler.fluesse2_bok_line_5_left3
union
select a.id, 0 as length, a.the_geom from eler.fluesse2_bok_line_5_left a full join eler.fluesse2_bok_line_5_left3 b on a.id = b.id where b.id is null order by id;

CREATE INDEX fluesse2_bok_line_5_left4_index_geom ON eler.fluesse2_bok_line_5_left4 USING gist (the_geom);


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_buffer_collect;
create table eler.fluesse2_bok_buffer_collect as 
select  a.id as id_right, b.id as id_left, case when a.length = b.length then 'left' else 
		case when a.length > b.length then 'left' else 'right' end end as outside,
case when a.length = b.length then 'right' else 
		case when a.length > b.length then 'right' else 'left' end end as inside

 from eler.fluesse2_bok_line_5_right4 a inner join eler.fluesse2_bok_line_5_left4 b on a.id = b.id;


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

drop table if exists eler.fluesse2_bok_buffer_5_out;
create table eler.fluesse2_bok_buffer_5_out as 
select a.id, case when a.length = b.length then b.the_geom else 
		case when a.length > b.length then b.the_geom else a.the_geom end end as the_geom from eler.fluesse2_bok_line_5_right4 a inner join eler.fluesse2_bok_line_5_left4 b on a.id = b.id;

drop table if exists eler.fluesse2_bok_buffer_5_in;
create table eler.fluesse2_bok_buffer_5_in as 
select a.id, case when a.length = b.length then a.the_geom else 
		case when a.length > b.length then a.the_geom else b.the_geom end end as the_geom from eler.fluesse2_bok_line_5_right4 a inner join eler.fluesse2_bok_line_5_left4 b on a.id = b.id;


/*
drop table if exists eler.fluesse2_bok_line_5_right;
drop table if exists eler.fluesse2_bok_line_5_right2;
drop table if exists eler.fluesse2_bok_line_5_right3;
drop table if exists eler.fluesse2_bok_line_5_right4;

drop table if exists eler.fluesse2_bok_line_5_left;
drop table if exists eler.fluesse2_bok_line_5_left2;
drop table if exists eler.fluesse2_bok_line_5_left3;
drop table if exists eler.fluesse2_bok_line_5_left4;
*/
---------------------------------------------------------------

/*drop table if exists eler.owk_neigung;
create table eler.owk_neigung as 
select 1000000+id as id, 'desn_5371488' as owk, hang::numeric as value, the_geom from eler.owk_desn_5371488_neigung
union
select 2000000+id as id, 'desn_537192' as owk, hang::numeric as value, the_geom from eler.owk_desn_537192_neigung
union
select 3000000+id as id, 'desn_537368' as owk, hang::numeric as value, the_geom from eler.owk_desn_537368_neigung
union
select 4000000+id as id, 'desn_54138' as owk, hang::numeric as value, the_geom from eler.owk_desn_54138_neigung
union
select 5000000+id as id, 'desn_542688' as owk, hang::numeric as value, the_geom from eler.owk_desn_542688_neigung
union
select 6000000+id as id, 'desn_5666332' as owk, hang::numeric as value, the_geom from eler.owk_desn_5666332_neigung
union
select 7000000+id as id, 'desn_537346' as owk, hang::numeric as value, the_geom from eler.owk_desn_537346_neigung;


CREATE INDEX owk_neigung_index_geom ON eler.owk_neigung USING gist (the_geom);*/



select owk, st_srid(the_geom) from eler.owk_neigung group by st_srid(the_geom), owk

select st_srid(the_geom) from eler.owk_desn_5371488_neigung group by st_srid(the_geom)

drop table if exists eler.fluesse2_bok_buffer_5_out_acker;
create table eler.fluesse2_bok_buffer_5_out_acker as 
select a.id, st_intersection(a.the_geom, b.the_geom) as the_geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse2_bok_buffer_5_out a inner join eler.landnutzung b on a.the_geom && b.the_geom
where st_intersects(a.the_geom, b.the_geom) = true and landuse = 'Acker';

drop table if exists eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5;
create table eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5 as 
select a.id, st_intersection(a.the_geom, b.the_geom) as the_geom, st_area(st_intersection(a.the_geom, b.the_geom)) as area from eler.fluesse2_bok_buffer_5_out_acker a inner join eler.owk_neigung b on a.the_geom && b.the_geom
where st_intersects(a.the_geom, b.the_geom) = true and b.value >= 5.0;


drop table if exists eler.fluesse2_bok_buffer_5_out_acker_owk;
create table eler.fluesse2_bok_buffer_5_out_acker_owk as 
select owk, name, count(area) as count, sum(area), st_union(the_geom) as the_geom from(
	select b.de as owk, b.description_text as name, a.id, st_area(st_intersection(a.the_geom, b.the_geom)) as area, st_intersection(a.the_geom, b.the_geom) as the_geom 
	from eler.fluesse2_bok_buffer_5_out_acker a inner join eler.owk b on a.the_geom && b.the_geom
	where st_intersects(a.the_geom, b.the_geom) = true
) a group by owk, name order by owk, name;


drop table if exists eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5_owk;
create table eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5_owk as 
select owk, name, count(area) as count, sum(area), st_union(the_geom) as the_geom from(
	select b.de as owk, b.description_text as name, a.id, st_area(st_intersection(a.the_geom, b.the_geom)) as area, st_intersection(a.the_geom, b.the_geom) as the_geom
	from eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5 a inner join eler.owk b on a.the_geom && b.the_geom
	where st_intersects(a.the_geom, b.the_geom) = true
) a group by owk, name order by owk, name; 


drop table if exists eler.import_sc_param_grs_bok;
create table eler.import_sc_param_grs_bok as
select a.owk, a.name, round(a.sum::numeric/10000.0,2) as acker_ha, 
round(b.sum::numeric/10000.0,2) as acker_fehlender_randsterifen_ha, 
round(b.sum::numeric/a.sum::numeric*100.0,2) as diff_rand_proz 
from eler.fluesse2_bok_buffer_5_out_acker_owk a inner join eler.fluesse2_bok_buffer_5_out_acker_hn_groesser5_owk b on a.owk = b.owk;


drop table if exists eler.import_sc_param_all;
create table eler.import_sc_param_all as
select b.idarea_data, area_data, description_text, fl_ist, fl_50, fl_100, diff_rand_proz, fl_ist+diff_rand_proz as fl_bok, b.the_geom  from eler.import_sc_param_grs_bok a inner join eler.import_sc_param_grs b on a.owk = b.area_data



