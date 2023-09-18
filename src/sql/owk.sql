select a.*, b.the_geom from spatial.area_data a inner join spatial.area_geom b on a.idarea_data = b.idarea_data where a.idarea = 26
and (de = 'DESN_542688' or de = 'DESN_537368' or de = 'DESN_537192'
or description_text like '%Bahre%'
or description_text like '%Mehltheuer%'
or description_text like '%Döbitzbach%'
or description_text like '%Wildenfelser%'

)