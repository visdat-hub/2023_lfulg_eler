--------------------------------------------------
--------------------------------------------------
-- zwischenfrucht -- scenario
--------------------------------------------------
--------------------------------------------------
select hkcode from eler.feldbloecke_eler_2021 where al4_fl > 0 and jahr = 2018 group by hkcode

-- "112" - Winterhartweizen (Durum)
-- "115" - Winterweichweizen
-- "116" - Sommerweichweizen
-- "121" - Winterroggen, Winter-Waldstaudenroggen
-- "131" - Wintergerste
-- "311" - Winterraps

-- bei 176 (al_4_100 = Eler AL 4 100% Sommerung) und 175 (al_4_50 = Eler AL 4 50% Sommerung)

-- 174 --> al_4_ist --> Eler AL 4 Ist
-- 174 --> nur auf acker
-- 174 --> konservierende BB (25) aus 2018 (1410)
-- 174 --> direktsaat (520) aus 2018 (1410)
-- 174 --> zwischenfrucht (501) = zf_ist(neu)
-- 174 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

-- 175 --> konservierende BB (25) aus 2018 (1410) 
-- 175 --> zwischenfrucht (501) = zf_sommer_50(neu)
-- 175 --> direktsaat (520) aus 2018 (1410)
-- 175 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

-- 176 --> konservierende BB (25) aus 2018 (1410) 
-- 176 --> zwischenfrucht (501) = zf_sommer_100(neu)
-- 176 --> direktsaat (520) aus 2018 (1410)
-- 176 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

-- Wasserbilanz bleibt für alle Scenarien gleich
drop table if exists tmp_zf;
create temp table tmp_zf as
select a.*, c.the_geom from ( 
	select b.owk_id, b.owk_name, round(al4_fl*100/fl,2) as zf_ist, al4_fl, fl from (
		select owk_id, owk_name, round(sum(al4_fl)::numeric,2) as al4_fl from eler.feldbloecke_eler_2021 where al4_fl > 0 and jahr = 2018 group by owk_id, owk_name
	) a full join (
		select owk_id, owk_name, round(sum(shape_area/1000.0)::numeric,2) as fl,round(sum(st_area(the_geom)/1000.0)::numeric,2) as fl1 from eler.feldbloecke_eler_2021 group by owk_id, owk_name
	) b on a.owk_id = b.owk_id 
) a inner join spatial.area_data b on a. owk_id = b.de inner join spatial.area_geom c on b.idarea_data = c.idarea_data where idarea = 26
-- problem
select owk_id, owk_name, round(al4_fl::numeric,2) as al4_fl, round((shape_area/10000.0)::numeric,2) as fl, round(al4_fl::numeric,2)-round((shape_area/10000.0)::numeric,2) as diff, round((st_area(the_geomgeom)/10000.0)::numeric,2) 
from eler.feldbloecke_eler_2021 where al4_fl > 0 and jahr = 2018

--------------------------------------------------
-- db stb_sachsen_copy
-- sommerung (idfrucht = 4 or idfrucht = 5 or idfrucht = 6 or idfrucht = 7 or idfrucht = 8 or idfrucht = 9 or idfrucht = 21 or idfrucht = 22)
-- aus db stb_sachsen_copy --> lwd.hkcode_stoffbilanzs

--CREATE EXTENSION dblink;
SELECT dblink_connect('myconn', 'dbname=stb_sachsen_copy');

drop table if exists tmp01;
create temp table tmp01 as
select * from 
	dblink('myconn', 'select idfrucht, round(proz,2) as proz, de::text, description_text::text from ldw."15_18_area" a inner join spatial.area_data b on a.idarea_data = b.idarea_data where year = 2018
	and (de = ''DESN_542688'' or de = ''DESN_537368'' or de = ''DESN_537192''
	or description_text like ''%Bahre%''
	or description_text like ''%Mehltheuer%''
	or description_text like ''%Döbitzbach%''
	or description_text like ''%Wildenfelser%''
	)') AS (idfrucht int, proz numeric, de text, description_text text);


select de, description_text, sum(proz) as sum from tmp01 group by de, description_text 

-- sommer
drop table if exists tmp_zf_sommer;
create temp table tmp_zf_sommer as
select de as owk_id, description_text, sum(proz) as zf_sommer_100, round(sum(proz)*0.5,2) as zf_sommer_50 from tmp01 
where idfrucht = 4 or idfrucht = 5 or idfrucht = 6 or idfrucht = 7 or idfrucht = 8 or idfrucht = 9 or idfrucht = 21 or idfrucht = 22 group by de, description_text 


--------------------------------------------------
--------------------------------------------------
-- direktsaat -- scenario
--------------------------------------------------
--------------------------------------------------
select hkcode from eler.feldbloecke_eler_2021 where al2_fl > 0 and jahr = 2018 group by hkcode

-- "411" - Silomais (als Hauptfutter)

-- 171 --> al_2_ist --> Eler AL2 AL4 Ist
-- 171 --> nur auf acker
-- 171 --> konservierende BB (25) aus 2018 (1410) 
-- 171 --> direktsaat (520) = ds_ist(neu)
-- 171 --> zwischenfrucht (501) aus 2018 (1410) + untersaat aus 2018 (1410)
-- 171 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

-- 172 --> al_2_50 --> ?
-- 172 --> nur auf acker
-- 172 --> konservierende BB (25) = 0
-- 172 --> direktsaat = direktsaat (520) aus 2018 (1410) + konservierende BB aus 2018 (1410)
-- 172 --> zwischenfrucht (501) = zf_ist(neu)
-- 172 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

-- 173 --> al_2_100 --> Eler AL 2 100%
-- 173 --> nur auf acker
-- 173 --> konservierende BB (25) = 0
-- 173 --> direktsaat (520) = 100%
-- 173 --> zwischenfrucht (501) aus 2018 (1410) + untersaat aus 2018 (1410)
-- 173 --> Grünstreifen in Ppart mit 40% Minderung auf 14 % der Ackerfläche (0,4*0,14 = 5,6% Minderung) -- nur zur info

drop table if exists tmp_ds;
create temp table tmp_ds as
select b.owk_id, b.owk_name, round(al2_fl*100/fl,2) as ds_ist, 50.0 as ds_50, 100.0 as ds_100 from (
	select owk_id, owk_name, round(sum(al2_fl)::numeric,2) as al2_fl from eler.feldbloecke_eler_2021 where al2_fl > 0 and jahr = 2018 group by owk_id, owk_name
) a full join (
	select owk_id, owk_name, round(sum(shape_area/1000.0)::numeric,2) as fl from eler.feldbloecke_eler_2021 group by owk_id, owk_name
) b on a.owk_id = b.owk_id

select owk_id, owk_name, round(al2_fl::numeric,2) as al2_fl, round((shape_area/10000.0)::numeric,2) as fl, round(al2_fl::numeric,2)-round((shape_area/10000.0)::numeric,2) as diff, round((st_area(the_geom)/10000.0)::numeric,2) 
from eler.feldbloecke_eler_2021 where al2_fl > 0 and jahr = 2018 and jahr = 2018


drop table if exists tmp_neu;
create temp table tmp_neu as
select a.owk_id, a.owk_name, zf_ist, zf_sommer_50, zf_sommer_100, ds_ist, ds_50, ds_100, the_geom from tmp_zf a inner join tmp_zf_sommer b on a.owk_id = b.owk_id inner join tmp_ds c on a.owk_id = c.owk_id


/*
drop table if exists eler.import_kbb_2018;
create table eler.import_kbb_2018 as
SELECT a.idarea_data, a.area_data as owk_id, description_text as name, kbb as kbb_2018, zf as zf_2018, usaat as usaat_2018, dsaat as dsaat_2018, c.the_geom FROM spatial.area_data a
INNER JOIN (
	SELECT a.idarea_data, c.value AS dsaat, the_geom FROM spatial.area_data a
	INNER JOIN spatial.area_geom b ON a.idarea_data = b.idarea_data
	INNER JOIN (SELECT idarea, idarea_data, sum(count*mean)/ sum(count) AS value FROM edit.sbvf_statistics_base(
		'{"idlevel": 3, "idarea": 26, "idparam_groupby": ""}',
		'{"idparam": 520, "idscenario": 1410, "model_year":"2018", "model_scenario_name":"fb01_yearly02"}',
		'{"base_dir": "/mnt/galfdaten/daten_stb/", "model_project_name": "stb_sachsen"}'
	)  WHERE count > 0 GROUP BY idarea, idarea_data) c ON a.idarea_data = c.idarea_data
) c on a.idarea_data = c.idarea_data INNER JOIN (
	SELECT a.idarea_data, c.value AS usaat, the_geom FROM spatial.area_data a
	INNER JOIN spatial.area_geom b ON a.idarea_data = b.idarea_data
	INNER JOIN (SELECT idarea, idarea_data, sum(count*mean)/ sum(count) AS value FROM edit.sbvf_statistics_base(
		'{"idlevel": 3, "idarea": 26, "idparam_groupby": ""}',
		'{"idparam": 519, "idscenario": 1410, "model_year":"2018", "model_scenario_name":"fb01_yearly02"}',
		'{"base_dir": "/mnt/galfdaten/daten_stb/", "model_project_name": "stb_sachsen"}'
	)  WHERE count > 0 GROUP BY idarea, idarea_data) c ON a.idarea_data = c.idarea_data
) d on a.idarea_data = d.idarea_data INNER JOIN (
	SELECT a.idarea_data, c.value AS kbb, the_geom FROM spatial.area_data a
	INNER JOIN spatial.area_geom b ON a.idarea_data = b.idarea_data
	INNER JOIN (SELECT idarea, idarea_data, sum(count*mean)/ sum(count) AS value FROM edit.sbvf_statistics_base(
		'{"idlevel": 3, "idarea": 26, "idparam_groupby": ""}',
		'{"idparam": 25, "idscenario": 1410, "model_year":"2018", "model_scenario_name":"fb01_yearly02"}',
		'{"base_dir": "/mnt/galfdaten/daten_stb/", "model_project_name": "stb_sachsen"}'
	)  WHERE count > 0 GROUP BY idarea, idarea_data) c ON a.idarea_data = c.idarea_data
) e on a.idarea_data = e.idarea_data INNER JOIN (
	SELECT a.idarea_data, c.value AS zf, the_geom FROM spatial.area_data a
	INNER JOIN spatial.area_geom b ON a.idarea_data = b.idarea_data
	INNER JOIN (SELECT idarea, idarea_data, sum(count*mean)/ sum(count) AS value FROM edit.sbvf_statistics_base(
		'{"idlevel": 3, "idarea": 26, "idparam_groupby": ""}',
		'{"idparam": 501, "idscenario": 1410, "model_year":"2018", "model_scenario_name":"fb01_yearly02"}',
		'{"base_dir": "/mnt/galfdaten/daten_stb/", "model_project_name": "stb_sachsen"}'
	)  WHERE count > 0 GROUP BY idarea, idarea_data) c ON a.idarea_data = c.idarea_data
) f on a.idarea_data = f.idarea_data
WHERE a.area_data = 'DESN_542688' or a.area_data = 'DESN_537368' or a.area_data = 'DESN_537192'
	or description_text like '%Bahre%'
	or description_text like '%Mehltheuer%'
	or description_text like '%Döbitzbach%'
	or description_text like '%Wildenfelser%'


select * from eler.import_kbb_2018
*/

drop table if exists tmp_neu2;
create temp table tmp_neu2 as
select a.owk_id, a.owk_name, zf_ist, zf_sommer_50, zf_sommer_100, ds_ist, ds_50, ds_100, round(zf_2018,2) as zf_2018, round(kbb_2018,2) as kbb_2018, round(usaat_2018,2) as usaat_2018, 
round(dsaat_2018,2) as dsaat_2018, st_intersection(a.the_geom, b.the_geom) as the_geom 
from tmp_neu a inner join eler.import_kbb_2018 b on a.the_geom && b.the_geom where st_intersects(a.the_geom, b.the_geom)

drop table if exists eler.import_sc_param;
create table eler.import_sc_param as

select a.owk_id, a.owk_name, 
kbb_2018,
dsaat_2018,
zf_2018,

kbb_2018 as "168_kbb", 
dsaat_2018 as "168_dsaat", 
zf_2018 as "168_zf",

kbb_2018 as "169_kbb", 
dsaat_2018 as "169_dsaat", 
zf_2018 as "169_zf",

kbb_2018 as "170_kbb", 
dsaat_2018 as "170_dsaat", 
zf_2018 as "170_zf",

kbb_2018 as "171_kbb", 
case when ds_ist is null then 0.0 else ds_ist end as "171_dsaat", 
zf_2018 as "171_zf",

0.0 as "172_kbb", 
kbb_2018+ case when ds_ist is null then 0.0 else ds_ist end as "172_dsaat", 
zf_2018 as "172_zf",

0.0 as "173_kbb", 
100.0 as "173_dsaat", 
zf_2018 as "173_zf",

kbb_2018 as "174_kbb", 
dsaat_2018 as "174_dsaat", 
case when zf_ist is null then 0.0 else zf_ist end as "174_zf",

kbb_2018 as "175_kbb", 
dsaat_2018 as "175_dsaat", 
zf_sommer_50 as "175_zf",

kbb_2018 as "176_kbb", 
dsaat_2018 as "176_dsaat", 
zf_sommer_100 as "176_zf",

0.05 as cfaktor_dsaat,
0.06 as cfaktor_kbb,
0.07 as cfaktor_zf, the_geom

from tmp_neu2 a



select 
"171_zf" as "171_alt_zf", case when  ("171_kbb"+ "171_dsaat" + "171_zf") <= 100.0 then "171_zf" else "171_zf" + (100.0-("171_kbb"+ "171_dsaat" + "171_zf")) end as "zf_neu_171", "171_kbb"+ "171_dsaat" + "171_zf" as "all_171",
"172_zf" as "172_alt_zf", case when  ("172_kbb"+ "172_dsaat" + "172_zf") <= 100.0 then "172_zf" else "172_zf" + (100.0-("172_kbb"+ "172_dsaat" + "172_zf")) end as "zf_neu_172", "172_kbb"+ "172_dsaat" + "172_zf" as "all_172",
"173_zf" as "173_alt_zf", case when  ("173_kbb"+ "173_dsaat" + "173_zf") <= 100.0 then "173_zf" else "173_zf" + (100.0-("173_kbb"+ "173_dsaat" + "173_zf")) end as "zf_neu_173", "173_kbb"+ "173_dsaat" + "173_zf" as "all_173",
"174_zf" as "174_alt_zf", case when  ("174_kbb"+ "174_dsaat" + "174_zf") <= 100.0 then "174_zf" else "174_zf" + (100.0-("174_kbb"+ "174_dsaat" + "174_zf")) end as "zf_neu_174", "174_kbb"+ "174_dsaat" + "174_zf" as "all_174",
"175_zf" as "175_alt_zf", case when  ("175_kbb"+ "175_dsaat" + "175_zf") <= 100.0 then "175_zf" else "175_zf" + (100.0-("175_kbb"+ "175_dsaat" + "175_zf")) end as "zf_neu_175", "175_kbb"+ "175_dsaat" + "175_zf" as "all_175",
"176_zf" as "176_alt_zf", case when  ("176_kbb"+ "176_dsaat" + "176_zf") <= 100.0 then "176_zf" else "176_zf" + (100.0-("176_kbb"+ "176_dsaat" + "176_zf")) end as "zf_neu_176", "176_kbb"+ "176_dsaat" + "176_zf" as "all_176",  (100.0-("176_kbb"+ "176_dsaat" + "176_zf"))
from eler.import_sc_param




