/****** Testing through Rarity Analysis Query SQL_Queries_For_Data ******/

------------------------------------------------------------------------
-- just a summary of species' distribution 
SELECT 
		LEFT(lu_boundary_species.species_cd, 1)
		 + UPPER(SUBSTRING(lu_boundary_species.species_cd, 2, 4))
		 + RIGHT(lu_boundary_species.species_cd, 1) AS spp,
		SUM(lu_boundary_species.count) AS sum_count
FROM	lu_boundary_species
GROUP BY lu_boundary_species.species_cd
ORDER BY spp;

-- only 1718 species reported - missing mSPOGx

------------------------------------------------------------------------

-- List the number of species in lu_boundary_species table
SELECT DISTINCT [species_cd]
  FROM [GAP_AnalyticDB].[dbo].[lu_boundary_species];

-- 1719 records

------------------------------------------------------------------------
-- List the number of hucs in analysis query

        SELECT DISTINCT 
			   lu_boundary.hucs,
			   hucs.huc12rng
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid

-- 82717 records

------------------------------------------------------------------------
-- First two tables of sel_hucs and dist_spp for missing species mSPOGx

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid)
			  --WHERE  (*****Insert HUC List*****)

--dist_spp AS (
    SELECT TOP (100) PERCENT 
               lu_boundary_species.count, 
               sel_hucs_1.hucs, 
               sel_hucs_1.huc12rng, 
               lu_boundary_species.species_cd, 
               sel_hucs_1.padus1_4
        FROM sel_hucs AS sel_hucs_1 
             INNER JOIN lu_boundary_species
              ON sel_hucs_1.value = lu_boundary_species.boundary
		WHERE lu_boundary_species.species_cd = 'mSPOGx'
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng;

-- 115 records, none of which have a padus1_4 id

------------------------------------------------------------------------
-- Added next table total_cnt_spp 

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid),

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
		WHERE lu_boundary_species.species_cd = 'mSPOGx'
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng) 

-- total_cnt_spp AS (        
    SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               tblTaxa.strTaxaLetter, 
			   tblTaxa.strUC,
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
                 tblTaxa.strUC, 
                 dist_spp_3.species_cd;

-- NO OUTPUT AS THERE ARE NO PIXEL ON ANY PADUS1_4 POLYGONS
        
------------------------------------------------------------------------
-- Changed INNER TO LEFT JOIN for dist_spp_3.padus1_4 = padus1_4
--   to pick up records not associated with any padus1_4 records

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid),

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
		WHERE lu_boundary_species.species_cd = 'mSPOGx'
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng) 
        
    SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               tblTaxa.strTaxaLetter, 
			   tblTaxa.strUC,
               dist_spp_3.species_cd, 
               SUM(dist_spp_3.count) AS total_spp_count
        FROM dist_spp AS dist_spp_3 
             INNER JOIN tblTaxa
              ON dist_spp_3.species_cd = tblTaxa.strUC 
             LEFT JOIN padus1_4
              ON dist_spp_3.padus1_4 = padus1_4.objectid
        GROUP BY dist_spp_3.hucs, 
                 dist_spp_3.huc12rng, 
                 tblTaxa.strTaxaLetter,
                 tblTaxa.strUC, 
                 dist_spp_3.species_cd;
        
-- 47 records

------------------------------------------------------------------------
-- Removed tblTaxa referencing to increase query efficiency

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid),

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
		--WHERE lu_boundary_species.species_cd = 'mSPOGx'
        ORDER BY sel_hucs_1.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs_1.padus1_4,
                 sel_hucs_1.huc12rng) 
        
    SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               UPPER(LEFT(dist_spp_3.species_cd, 1)) AS strTaxaLetter, 
			   dist_spp_3.species_cd, 
               SUM(dist_spp_3.count) AS total_spp_count
        FROM dist_spp AS dist_spp_3 
             LEFT JOIN padus1_4
              ON dist_spp_3.padus1_4 = padus1_4.objectid
		WHERE UPPER(LEFT(dist_spp_3.species_cd, 1)) = 'A'
        GROUP BY dist_spp_3.hucs, 
                 dist_spp_3.huc12rng, 
                 dist_spp_3.species_cd;

------------------------------------------------------------------------
-- Added spp_pad# tables and changed suffixes for CTEs to match gap
--   status, more for readability than anything else 

    WITH 
    sel_hucs AS (
        SELECT lu_boundary.value, 
               hucs.objectid, 
               hucs.huc12rng, 
               lu_boundary.padus1_4, 
               lu_boundary.hucs
        FROM lu_boundary 
             INNER JOIN hucs
              ON lu_boundary.hucs = hucs.objectid),

    dist_spp AS (
        SELECT TOP (100) PERCENT 
               lu_boundary_species.count, 
               sel_hucs.hucs, 
               sel_hucs.huc12rng, 
               lu_boundary_species.species_cd, 
               sel_hucs.padus1_4
        FROM sel_hucs 
             INNER JOIN lu_boundary_species
              ON sel_hucs.value = lu_boundary_species.boundary
		--WHERE lu_boundary_species.species_cd = 'mSPOGx'
        ORDER BY sel_hucs.hucs,
                 lu_boundary_species.species_cd, 
                 sel_hucs.padus1_4,
                 sel_hucs.huc12rng), 
        
    total_cnt_spp AS (
	    SELECT dist_spp_0.hucs, 
               dist_spp_0.huc12rng, 
               UPPER(LEFT(dist_spp_0.species_cd, 1)) AS strTaxaLetter, 
			   dist_spp_0.species_cd, 
               SUM(dist_spp_0.count) AS total_spp_count
        FROM dist_spp AS dist_spp_0 
             LEFT JOIN padus1_4 AS padus1_4_0
              ON dist_spp_0.padus1_4 = padus1_4_0.objectid
        GROUP BY dist_spp_0.hucs, 
                 dist_spp_0.huc12rng, 
                 dist_spp_0.species_cd),        

    spp_pad1 AS (
        SELECT dist_spp_1.hucs, 
               dist_spp_1.huc12rng, 
               UPPER(LEFT(dist_spp_1.species_cd, 1)) AS strTaxaLetter, 
			   dist_spp_1.species_cd, 
               SUM(dist_spp_1.count) AS padstat1_count
        FROM dist_spp AS dist_spp_1 
             LEFT JOIN padus1_4 AS padus1_4_1 
              ON dist_spp_1.padus1_4 = padus1_4_1.objectid
        WHERE (RTRIM(LTRIM(padus1_4_1.gap_sts)) = '1')
        GROUP BY dist_spp_1.hucs, 
                 dist_spp_1.huc12rng, 
                 dist_spp_1.species_cd),
	    
    spp_pad2 AS (
        SELECT dist_spp_2.hucs, 
               dist_spp_2.huc12rng, 
               UPPER(LEFT(dist_spp_2.species_cd, 1)) AS strTaxaLetter, 
			   dist_spp_2.species_cd, 
               SUM(dist_spp_2.count) AS padstat2_count
        FROM dist_spp AS dist_spp_2 
             LEFT JOIN padus1_4 AS padus1_4_2 
              ON dist_spp_2.padus1_4 = padus1_4_2.objectid
        WHERE (RTRIM(LTRIM(padus1_4_2.gap_sts)) = '2')
        GROUP BY dist_spp_2.hucs, 
                 dist_spp_2.huc12rng, 
                 dist_spp_2.species_cd), 
                 
    spp_pad3 AS (
        SELECT dist_spp_3.hucs, 
               dist_spp_3.huc12rng, 
               UPPER(LEFT(dist_spp_3.species_cd, 1)) AS strTaxaLetter, 
			   dist_spp_3.species_cd, 
               SUM(dist_spp_3.count) AS padstat3_count
        FROM dist_spp AS dist_spp_3 
             LEFT JOIN padus1_4 AS padus1_4_3 
              ON dist_spp_3.padus1_4 = padus1_4_3.objectid
        WHERE (RTRIM(LTRIM(padus1_4_3.gap_sts)) = '3')
        GROUP BY dist_spp_3.hucs, 
                 dist_spp_3.huc12rng, 
                 dist_spp_3.species_cd), 
                 
    spp_pad4 AS (
        SELECT dist_spp_4.hucs, 
               dist_spp_4.huc12rng, 
               UPPER(LEFT(dist_spp_4.species_cd, 1)) AS strTaxaLetter,
               dist_spp_4.species_cd, 
               SUM(dist_spp_4.count) AS padstat4_count
        FROM dist_spp AS dist_spp_4 
             LEFT JOIN padus1_4 AS padus1_4_4 
              ON dist_spp_4.padus1_4 = padus1_4_4.objectid
        WHERE (RTRIM(LTRIM(padus1_4_4.gap_sts)) = '4')
        GROUP BY dist_spp_4.hucs, 
                 dist_spp_4.huc12rng, 
                 dist_spp_4.species_cd)
     
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
    FROM total_cnt_spp 
         LEFT OUTER JOIN spp_pad3 
          ON total_cnt_spp.hucs = spp_pad3.hucs AND 
             total_cnt_spp.huc12rng = spp_pad3.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad3.species_cd 
         LEFT OUTER JOIN spp_pad2
          ON total_cnt_spp.hucs = spp_pad2.hucs AND
             total_cnt_spp.huc12rng = spp_pad2.huc12rng AND
             total_cnt_spp.species_cd = spp_pad2.species_cd 
         LEFT OUTER JOIN spp_pad4
          ON total_cnt_spp.hucs = spp_pad4.hucs AND 
             total_cnt_spp.huc12rng = spp_pad4.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad4.species_cd 
         LEFT OUTER JOIN spp_pad1
          ON total_cnt_spp.hucs = spp_pad1.hucs AND 
             total_cnt_spp.huc12rng = spp_pad1.huc12rng AND 
             total_cnt_spp.species_cd = spp_pad1.species_cd


-- 21,613,984 records
-- 00:43:04 to run on BaSIC SQL Server