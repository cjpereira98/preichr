WITH physical_containers_details AS (SELECT ocp.snapshot_date,
                                            ocp.warehouse_id             AS dest_fc,
                                            ocp.scannable_id             AS child_scannable_id,
                                            ocp.container_id             AS child_container_id,
                                            ocp.containing_container_id  AS child_containing_container_id,
                                            ocp.container_type           AS child_container_type,
                                            MAX(ocp.dw_last_updated)     AS child_dw_last_updated,
                                            ocp2.container_id            AS parent_level_container_id,
                                            ocp2.scannable_id            AS parent_level_scannable_id,
                                            ocp2.containing_container_id AS parent_level_containing_container_id,
                                            ocp2.container_type          AS parent_level_container_type


                                     FROM namek.aftbi_ddl.o_containers_physical ocp

                                              LEFT JOIN namek.aftbi_ddl.o_containers_physical ocp2
                                                        ON ocp.containing_container_id = ocp2.container_id
                                                            AND ocp.warehouse_id = ocp2.warehouse_id
                                                            AND ocp.snapshot_date = ocp2.snapshot_date

                                     WHERE ocp.warehouse_id IN (SELECT warehouse_id
                                             FROM andes_bi.qubit_bi.camp_fcs
                                             WHERE warehouse_type IN ('IXD') AND is_active IN ('true'))
                                       AND ocp2.warehouse_id IN (SELECT warehouse_id
                                             FROM andes_bi.qubit_bi.camp_fcs
                                             WHERE warehouse_type IN ('IXD') AND is_active IN ('true'))
                                       AND ocp.container_type IN
                                           ('CASE', 'TOTE', 'PALLET', 'VIRTUALLY_LABELED_CASE', 'TRANSFER_TOTE')
                                       AND ocp.snapshot_date BETWEEN CURRENT_DATE - 4 AND CURRENT_DATE

                                     GROUP BY 1, 2, 3, 4, 5, 6, 8, 9, 10, 11

                                     ORDER BY ocp.snapshot_date DESC),

     trans_container_list AS (SELECT *

                              FROM physical_containers_details

                              WHERE LEFT(parent_level_scannable_id, 4) IN ('pk-x')
                                AND LEN(parent_level_scannable_id) = 14),

     manifest AS (SELECT DISTINCT tdi.creation_date::DATE,
                                  tdi.departure_datetime::DATE,
                                  tdi.arrival_datetime_utc::DATE,
                                  tdi.receive_datetime_utc::DATE,
                                  tdi.source_warehouse_id                                   AS source_fc,
                                  fcs.warehouse_type                                        AS source_fc_type,
                                  tdi.warehouse_id                                          AS dest_fc,
                                  fcd.warehouse_type                                        AS dest_fc_type,
                                  tdi.trailer_id                                            AS vrid,
                                  tdi.amazon_shipment_ref_id,
                                  tdi.transfer_delivery_status,
                                  tdi.transfer_delivery_id,
                                  (SUM(tdi.quantity_expected))                              AS total_quantity_manifested,
                                  (SUM(tdi.quantity_expected) - SUM(tdi.quantity_received)) AS manifest_qty_left_to_receive

                  FROM andes_bi.aftbi_ddl.d_transfer_delivery_items tdi

                           LEFT JOIN andes_bi.qubit_bi.camp_fcs fcs
                                     ON tdi.source_warehouse_id = fcs.warehouse_id

                           LEFT JOIN andes_bi.qubit_bi.camp_fcs fcd
                                     ON tdi.warehouse_id = fcd.warehouse_id

                  WHERE tdi.region_id IN ('1')
                    AND fcs.warehouse_type IN ('IXD')
                    AND fcd.warehouse_type IN ('IXD')
                    AND tdi.transfer_delivery_status NOT IN ('CLOSED', 'INBOUND')
                    AND tdi.receive_datetime_utc IS NOT NULL
                    AND tdi.creation_date >= '2024-02-01'
                    AND fcs.is_active IN ('true')
                    AND fcd.is_active IN ('true')
                    AND tdi.trailer_id NOT IN ('FOUND_SAME_FC','FOUND_SAME_FC_MANIFEST','FOUND_DIFFERENT_FC_MANIFEST','FOUND_IN_DIFFERENT_FC')


                  GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),


     containers AS (SELECT m.creation_date::DATE,
                           m.departure_datetime::DATE,
                           m.arrival_datetime_utc::DATE,
                           m.receive_datetime_utc::DATE,
                           m.source_fc,
                           m.source_fc_type,
                           m.dest_fc,
                           m.dest_fc_type,
                           m.amazon_shipment_ref_id,
                           m.vrid,
                           m.transfer_delivery_status,
                           m.transfer_delivery_id,
                           tci.scannable_id,
                           tci.container_status,
                           tci.container_type,
                           tci.container_item_quantity,
                           LEFT(tci.scannable_id, 3) AS container_prefix,
                           m.total_quantity_manifested,
                           m.manifest_qty_left_to_receive

                    FROM manifest m
                             LEFT JOIN andes_bi.aftbi_ddl.d_transfer_container_items tci
                                       ON m.transfer_delivery_id = tci.transfer_delivery_id
                                           AND m.dest_fc = tci.warehouse_id

                    WHERE tci.region_id IN ('1')
                      AND tci.warehouse_id IN (SELECT warehouse_id
                                             FROM andes_bi.qubit_bi.camp_fcs
                                             WHERE warehouse_type IN ('IXD') AND is_active IN ('true'))
                      AND tci.container_status IN ('RECEIVED', 'RECEIVED_OVERAGE', 'INBOUND', 'STOWED', 'SHORTAGE')


                    ORDER BY m.creation_date DESC),

     container_summary AS (SELECT creation_date::DATE,
                                  departure_datetime::DATE,
                                  arrival_datetime_utc::DATE,
                                  receive_datetime_utc::DATE,
                                  source_fc,
                                  source_fc_type,
                                  dest_fc,
                                  dest_fc_type,
                                  amazon_shipment_ref_id,
                                  vrid,
                                  transfer_delivery_status,
                                  transfer_delivery_id,
                                  scannable_id,
                                  container_status,
                                  container_type,
                                  SUM(container_item_quantity) AS total_container_item_qty,
                                  container_prefix,
                                  total_quantity_manifested,
                                  manifest_qty_left_to_receive

                           FROM containers c


                           GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19),

     agg AS (SELECT cs.*,
                    tcl.snapshot_date,
                    tcl.dest_fc AS dest_fc_2,
                    tcl.child_scannable_id,
                    tcl.child_container_id,
                    tcl.child_containing_container_id,
                    tcl.child_container_type,
                    tcl.child_dw_last_updated,
                    tcl.parent_level_container_id,
                    tcl.parent_level_scannable_id,
                    tcl.parent_level_containing_container_id,
                    tcl.parent_level_container_type


             FROM container_summary cs

                      LEFT JOIN trans_container_list tcl
                                ON cs.scannable_id = tcl.child_scannable_id
                                    AND cs.dest_fc = tcl.dest_fc


             ORDER BY cs.total_container_item_qty DESC),

     dedupe AS (SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY scannable_id ORDER BY snapshot_date DESC) AS rn

                FROM agg


                GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                         27,
                         28, 29, 30),

     agg_2 AS (SELECT *,
                      CASE
                          WHEN container_status IN ('RECEIVED', 'RECEIVED_OVERAGE')
                              AND snapshot_date IS NOT NULL
                              THEN 'Not Yet Stowed'
                          WHEN container_status IN ('INBOUND')
                              THEN 'Not Yet Received'
                          ELSE '---'
                          END AS for_reconcile_category

               FROM dedupe

               WHERE rn = 1)


SELECT *

FROM agg_2 a2

WHERE a2.for_reconcile_category IN ('Not Yet Stowed', 'Not Yet Received')