USE GAP_AnalyticDB;
GO

/*
SQL Query for SPP Gap Status By Huc
Used in Species Rarity Analysis

*/
 
/*
WITH 
sel_hucs AS (
	SELECT	lu_boundary.value, 
			hucs.objectid, 
			hucs.huc12rng, 
			lu_boundary.padus1_4, 
			lu_boundary.hucs
	FROM	lu_boundary INNER JOIN hucs 
			 ON lu_boundary.hucs = hucs.objectid
	WHERE  (*****Insert HUC List*****)
*/
--__________________________________________________________________________________________________________________

-- 

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid
        WHERE huc12rng like '10250017%'),
    
    dist_spp AS (
        SELECT TOP (100) PERCENT 
               lu_boundary_species.count, 
               sel_hucs_1.hucs, 
               sel_hucs_1.huc12rng, 
               lu_boundary_species.species_cd, 
               sel_hucs_1.padus1_4
        FROM sel_hucs AS sel_hucs_1 
             INNER JOIN lu_boundary_species
              ON sel_hucs_1.value = lu_boundary_species.boundary
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng), 
        
    total_cnt_spp AS (
        SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               tblTaxa.strTaxaLetter, 
               dist_spp_3.species_cd, 
               SUM(dist_spp_3.count) AS total_spp_count
        FROM dist_spp AS dist_spp_3 
             INNER JOIN tblTaxa
              ON dist_spp_3.species_cd = tblTaxa.strUC 
             INNER JOIN padus1_4
              ON dist_spp_3.padus1_4 = padus1_4.objectid
        GROUP BY dist_spp_3.hucs, 
                 dist_spp_3.huc12rng, 
                 tblTaxa.strTaxaLetter, 
                 dist_spp_3.species_cd), 
        
    spp_pad1 AS (
        SELECT dist_spp_2.hucs, 
               dist_spp_2.huc12rng, 
               tblTaxa_4.strTaxaLetter, 
               dist_spp_2.species_cd, 
               SUM(dist_spp_2.count) AS padstat1_count
        FROM dist_spp AS dist_spp_2 
             INNER JOIN tblTaxa AS tblTaxa_4
              ON dist_spp_2.species_cd = tblTaxa_4.strUC 
             INNER JOIN padus1_4 AS padus1_4_4 
              ON dist_spp_2.padus1_4 = padus1_4_4.objectid
        WHERE (RTRIM(LTRIM(padus1_4_4.gap_sts)) = '1')
        GROUP BY dist_spp_2.hucs, 
                 dist_spp_2.huc12rng, 
                 tblTaxa_4.strTaxaLetter, 
                 dist_spp_2.species_cd), 
    
    spp_pad2 AS (
        SELECT dist_spp_1.hucs, 
               dist_spp_1.huc12rng, 
               tblTaxa_3.strTaxaLetter, 
               dist_spp_1.species_cd, 
               SUM(dist_spp_1.count) AS padstat2_count
        FROM dist_spp AS dist_spp_1 
             INNER JOIN tblTaxa AS tblTaxa_3
              ON dist_spp_1.species_cd = tblTaxa_3.strUC 
             INNER JOIN padus1_4 AS padus1_4_3 
              ON dist_spp_1.padus1_4 = padus1_4_3.objectid
        WHERE (RTRIM(LTRIM(padus1_4_3.gap_sts)) = '2')
        GROUP BY dist_spp_1.hucs, 
                 dist_spp_1.huc12rng, 
                 tblTaxa_3.strTaxaLetter, 
                 dist_spp_1.species_cd), 
                 
    spp_pad3 AS (
        SELECT dist_spp.hucs, 
               dist_spp.huc12rng, 
               tblTaxa_2.strTaxaLetter, 
               dist_spp.species_cd, 
               SUM(dist_spp.count) AS padstat3_count
        FROM dist_spp AS dist_spp 
             INNER JOIN tblTaxa AS tblTaxa_2 
              ON dist_spp.species_cd = tblTaxa_2.strUC 
             INNER JOIN padus1_4 AS padus1_4_2 
              ON dist_spp.padus1_4 = padus1_4_2.objectid
        WHERE (RTRIM(LTRIM(padus1_4_2.gap_sts)) = '3')
        GROUP BY dist_spp.hucs, 
                 dist_spp.huc12rng, 
                 tblTaxa_2.strTaxaLetter, 
                 dist_spp.species_cd), 
                 
    spp_pad4 AS (
        SELECT dist_spp.hucs, 
               dist_spp.huc12rng, 
               tblTaxa_1.strTaxaLetter, 
               dist_spp.species_cd, 
               SUM(dist_spp.count) AS padstat4_count
        FROM dist_spp AS dist_spp 
             INNER JOIN tblTaxa AS tblTaxa_1 
              ON dist_spp.species_cd = tblTaxa_1.strUC 
             INNER JOIN padus1_4 AS padus1_4_1 
              ON dist_spp.padus1_4 = padus1_4_1.objectid
        WHERE (RTRIM(LTRIM(padus1_4_1.gap_sts)) = '4')
        GROUP BY dist_spp.hucs, 
                 dist_spp.huc12rng, 
                 tblTaxa_1.strTaxaLetter, 
                 dist_spp.species_cd)
     
    SELECT total_cnt_spp.strTaxaLetter AS Taxa, 
           LEFT(total_cnt_spp.species_cd, 1)
		    + UPPER(SUBSTRING(total_cnt_spp.species_cd, 2, 4))
			+ RIGHT(total_cnt_spp.species_cd, 1)  AS spp, 
           total_cnt_spp.huc12rng AS huc, 
           total_cnt_spp.total_spp_count AS spp_pixel_count, 
           spp_pad1.padstat1_count AS spp_gs1_pixel_count, 
           spp_pad2.padstat2_count AS spp_gs2_pixel_count, 
           spp_pad3.padstat3_count AS spp_gs3_pixel_count, 
           spp_pad4.padstat4_count AS spp_gs4_pixel_count, 
           COALESCE (spp_pad1.padstat1_count, 0) 
            + COALESCE (spp_pad2.padstat2_count, 0) 
            + COALESCE (spp_pad3.padstat3_count, 0) 
            + COALESCE (spp_pad4.padstat4_count, 0) AS spp_gs_total_check
    FROM total_cnt_spp AS total_cnt_spp 
         LEFT OUTER JOIN spp_pad3 AS spp_pad3 
          ON total_cnt_spp.hucs = spp_pad3.hucs AND 
             total_cnt_spp.huc12rng = spp_pad3.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad3.species_cd 
         LEFT OUTER JOIN spp_pad2 AS spp_pad2
          ON total_cnt_spp.hucs = spp_pad2.hucs AND
             total_cnt_spp.huc12rng = spp_pad2.huc12rng AND
             total_cnt_spp.species_cd = spp_pad2.species_cd 
         LEFT OUTER JOIN spp_pad4 AS spp_pad4
          ON total_cnt_spp.hucs = spp_pad4.hucs AND 
             total_cnt_spp.huc12rng = spp_pad4.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad4.species_cd 
         LEFT OUTER JOIN spp_pad1 AS spp_pad1
          ON total_cnt_spp.hucs = spp_pad1.hucs AND 
             total_cnt_spp.huc12rng = spp_pad1.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad1.species_cd
