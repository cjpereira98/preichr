function showView(view) {
    const viewContainer = document.getElementById("view-message");

    if (view === "Planner") {
        viewContainer.innerHTML = `
            <table border="1" cellpadding="5" cellspacing="0" class="headcount-table">
                <thead>
                    <tr>
                        <th>Line Item</th>
                        <th>Headcount</th>
                        <th>Hours</th>
                        <th>Jobs Input</th>
                        <th>Input CPH</th>
                        <th>Jobs Output</th>
                        <th>Output CPH</th>
                        <th>Units</th>
                        <th>UPH</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td><b>Inbound Transfer In (TI)</b></td></tr>
                <tr><td>Case Transfer In "98" HC</td></tr>
                <tr><td>Pallet Transfer In HC</td></tr>
                <tr><td><b>Decant</b></td></tr>
                <tr><td>Transfer In Decant HC</td></tr>
                <tr><td>Decant Non-TI HC</td></tr>
                <tr><td><b>RC Sort - Direct</b></td></tr>
                <tr><td>UIS 5lb Inductor HC</td></tr>
                <tr><td>UIS 20lb Inductor HC</td></tr>
                <tr><td>Manual Sort HC</td></tr>
                <tr><td><b>Transfer Out - Direct</b></td></tr>
                <tr><td>Manual Palletize HC</td></tr>
                <tr><td>Fluid Load (incl. Wall Builder) HC</td></tr>
                <tr><td><b>Transfer Out Dock - Direct</b></td></tr>
                <tr><td>Dock Pallet Loader HC</td></tr>
                <tr><td><b>Receive Dock</b></td></tr>
                <tr><td>Inbound Dock Clerk (RSVDC)</td></tr>
                <tr><td>Inbound Yard Driver (RSVIYD)</td></tr>
                <tr><td>PID Manual Divert (PIDMNDIV)</td></tr>
                <tr><td>PID Truck Unload (PIDTRUNL)</td></tr>
                <tr><td>Receive Dock Crew (RSVCRW)</td></tr>
                <tr><td>Receive Dock TDR (RSVTDR)</td></tr>
                <tr><td>Receive Line Loader (RSVLD)</td></tr>
                <tr><td>ReceiveLine Unloader (RSVULD)</td></tr>
                <tr><td>Vendor Cutter (VDRCUT)</td></tr>
                <tr><td>Vendor Line Load (VDRLRD)</td></tr>
                <tr><td><b>Receive-Support</b></td></tr>
                <tr><td>Case Rcv WaterSpider (CASEWATER)</td></tr>
                <tr><td>General Audits (GENAUDIT)</td></tr>
                <tr><td>Rcv WaterSpider (WATER)</td></tr>
                <tr><td>Receive 5S (RSV5S)</td></tr>
                <tr><td>MHE Support (MHERECS)</td></tr>
                <tr><td>Offline_Mods (OFFMODRS)</td></tr>
                <tr><td>IB Tote Replen (RSVRPL)</td></tr>
                <tr><td>PID Gatekeep (PIDGATEKEEP)</td></tr>
                <tr><td>Receive Ambassador (RAMB)</td></tr>
                <tr><td>Receive Dock Crew (RSDOCK)</td></tr>
                <tr><td>Receive Training (RSVTR)</td></tr>
                <tr><td><b>Transfer In Support</b></td></tr>
                <tr><td>TransferIn DockClerk (TITDC)</td></tr>
                <tr><td>Cart/Pallet Builder (PLTBLD)</td></tr>
                <tr><td>Line Load Injection (LINLNJT)</td></tr>
                <tr><td>TransferIn ToteStkng (TOTSTG)</td></tr>
                <tr><td>Cart Runner Trans (CRNTRA)</td></tr>
                <tr><td>Kermit Operator (KERMIT)</td></tr>
                <tr><td>Bin Scout Trans (BSCTRA)</td></tr>
                <tr><td>TransferIn Dock Crew (TRFICR)</td></tr>
                <tr><td>Trans Cart Run-Nike (NIKETRANSCART)</td></tr>
                <tr><td>Transfer In Ambssdr (TITA)</td></tr>
                <tr><td>Transfer In Training (TRFITR)</td></tr>
                <tr><td>Transfer In 5S (TRF5S)</td></tr>
                <tr><td><b>Prep Support</b></td></tr>
                <tr><td>Prep Ambassador (PREPAMB)</td></tr>
                <tr><td>Prep Kaizen (PRPKZN)</td></tr>
                <tr><td>Prep Omake (PRPOMK)</td></tr>
                <tr><td>Prep Training (PRPTR)</td></tr>
                <tr><td>Prep 5S (PRP5S)</td></tr>
                <tr><td><b>IB Problem Solve</b></td></tr>
                <tr><td>ATAC Problem Solve (ATACPS)</td></tr>
                <tr><td>Damage Processing (REBOX)</td></tr>
                <tr><td>Damages (DAMAGES)</td></tr>
                <tr><td>DecantProblemSolve (DCNTPS)</td></tr>
                <tr><td>DecantPsolveBacklog (DCNTPSBL)</td></tr>
                <tr><td>IB Sweeper (LPSWEEP)</td></tr>
                <tr><td>ISS Field Rep (ICVR)</td></tr>
                <tr><td>Receive ProblemSolve (IBPS)</td></tr>
                <tr><td>Stow Psolve Backlog (PSBKL)</td></tr>
                <tr><td>Stow to Prime Psolve (RECON)</td></tr>
                <tr><td>Prep Problem Solve (PREPPS)</td></tr>
                <tr><td><b>Dock Lead/PA</b></td></tr>
                <tr><td>Dock Lead/PA (LDOCK)</td></tr>
                <tr><td>Receive Lead/PA (RSLR)</td></tr>
                <tr><td><b>RC Sort</b></td></tr>
                <tr><td>AIS_5lb_Induct (AISOPSS)</td></tr>
                <tr><td>RC Sort 5S (RSRT5S)</td></tr>
                <tr><td>UIS 20lb Case Prep (UISCASEXL)</td></tr>
                <tr><td>UIS 20lb Psolve (UIS20PS)</td></tr>
                <tr><td>UIS 5lb Psolve (UIS5PS)</td></tr>
                <tr><td>UIS Case Prep (UISCASE)</td></tr>
                <tr><td>UIS SupUser 20lb (UIS20SU)</td></tr>
                <tr><td>UIS_5lb_ToteWrangle</td></tr>
                <tr><td>Water Spider (RCWS)</td></tr>
                <tr><td>RC Sort Ambassador (RCRSA)</td></tr>
                <tr><td>RC Sort Training (RSRTR)</td></tr>
                <tr><td><b>RC Presort</b></td></tr>
                <tr><td>RC Presort Cases HC (incl. DIVERTER)</td></tr>
                <tr><td><b>Transfer Out</b></td></tr>
                <tr><td>Robotic Water Spider (ROBWS)</td></tr>
                <tr><td>Robotics Operator (ROPER)</td></tr>
                <tr><td>Trans Out Overflow (OVRFLW)</td></tr>
                <tr><td>Transfer Out 5S (TRF5S)</td></tr>
                <tr><td>Water Spider (EOLWS)</td></tr>
                <tr><td>Offline_Mods (OFFMODXO)</td></tr>
                <tr><td>Robotic Problem Solve (ROBPS)</td></tr>
                <tr><td>Transfer Out Ambssdr (TOTOA)</td></tr>
                <tr><td>TransferOut Training (TRFOTR)</td></tr>
                <tr><td><b>Transfer Out Dock</b></td></tr>
                <tr><td>Shipping Clerk (SHPCL)</td></tr>
                <tr><td>TransferOut DockCrew (TRFOCR)</td></tr>
                <tr><td>Outbound Dock Crew (OUTCRW)</td></tr>
                <tr><td>Truck Loader (MTTL)</td></tr>
                <tr><td><b>Transfer Out Lead/PA</b></td></tr>
                <tr><td>RC Sort Lead/PA (RSRSL)</td></tr>
                <tr><td>Transfer Out Lead/PA</td></tr>
                <tr><td><b>Trans Out Prob Solve</b></td></tr>
                <tr><td>Fluid Load Sweep (FSWEEP)</td></tr>
                <tr><td>RC Sort ProblemSolve (PSRSPS)</td></tr>
                <tr><td>TransferOut Psolve (PSTOPS)</td></tr>
                <tr><td>Workflow (WRKFLOW)</td></tr>
                <tr><td><b>Each Receive</b></td></tr>
                <tr><td>Non-PID Conveyable (NPC) HC</td></tr>
                <tr><td>Each Receive Traditional HC</td></tr>
                <tr><td><b>LP Receive</b></td></tr>
                <tr><td>PrEditor Receive HC</td></tr>
                <tr><td><b>Pallet Receive NVF</b></td></tr>
                <tr><td>Pallet Receive HC</td></tr>
                <tr><td><b>Prep</b></td></tr>
                <tr><td>Prep Recorder Traditional HC</td></tr>
                <tr><td>Prep Pallet HC (incl. Prep Other)</td></tr>
                <tr><td>ATAC (Cubiscan) HC</td></tr>
                <tr><td><b>Totals</b></td></tr>
                    <!-- Add more rows here based on the content from the table -->
                </tbody>
            </table>
            <table border="1" cellpadding="5" cellspacing="0" class="assumption-table">
                <thead>
                    <tr>
                        <th>Assumption Line Item</th>
                        <th>Assumption Value</th>
                        <th>Historical Value</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td>Paid Hours</td></tr>
                <tr><td>PR CPP</td></tr>
                <tr><td>Divert:PC Ratio</td></tr>
                <tr><td>5# UPC In</td></tr>
                <tr><td>20# UPC In</td></tr>
                <tr><td>MS UPC In</td></tr>
                <tr><td>5# UPC Out</td></tr>
                <tr><td>20# UPC Out</td></tr>
                <tr><td>MS UPC Out</td></tr>
                <tr><td>NVF Decant Units per Case In</td></tr>
                <tr><td>TI Decant Units per Case In</td></tr>
                <tr><td>NVF Decant Units per Tote Out</td></tr>
                <tr><td>TI Decant Units per Tote Out</td></tr>
                <tr><td>Decant to Sort Unit Ratio</td></tr>
                <tr><td>% Decant Units TI</td></tr>
                <tr><td>% Decant Output Breaking to Sort</td></tr>
                <tr><td>% PID Cartons Breaking Eaches</td></tr>
                <tr><td>% PID Cartons Breaking Prep</td></tr>
                <tr><td>% FL OB Diverts</td></tr>
                <tr><td>% MP OB Diverts</td></tr>
                <tr><td>% Robots OB Diverts</td></tr>
                <tr><td>Diverts Created by PS per Shift</td></tr>
                <tr><td>Presort Cases per Shift</td></tr>
                <tr><td>CPP Robots</td></tr>
                <tr><td>CPP MP</td></tr>
                <!-- Add more rows here if necessary -->
                </tbody>
            </table>
            <table border="1" cellpadding="5" cellspacing="0" class="throughput-table">
                <thead>
                    <tr>
                        <th>Throughput Line Item</th>
                        <th>Throughput Value</th>
                        <th>Historical Value</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td>PID Cartons</td></tr>
                <tr><td>PR Pallets</td></tr>
                <tr><td>PR Cartons</td></tr>
                <tr><td>Combined Cartons</td></tr>
                <tr><td>Diverts</td></tr>
                <tr><td>CPLH w/o Support</td></tr>
                <tr><td>5# Units</td></tr>
                <tr><td>20# Units</td></tr>
                <tr><td>MS Units</td></tr>
                <tr><td>Total Sort Units</td></tr>
                </tbody>
            </table>
        `;
    } else if (view === "HC"){
        viewContainer.innerHTML = `
            <table border="1" cellpadding="5" cellspacing="0" class="headcount-table">
                <thead>
                    <tr>
                        <th>Line Item</th>
                        <th>Planned Headcount</th>
                        <th>Actual Headcount</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td><b>Inbound Transfer In (TI)</b></td></tr>
                <tr><td>Case Transfer In "98" HC</td></tr>
                <tr><td>Pallet Transfer In HC</td></tr>
                <tr><td><b>Decant</b></td></tr>
                <tr><td>Transfer In Decant HC</td></tr>
                <tr><td>Decant Non-TI HC</td></tr>
                <tr><td><b>RC Sort - Direct</b></td></tr>
                <tr><td>UIS 5lb Inductor HC</td></tr>
                <tr><td>UIS 20lb Inductor HC</td></tr>
                <tr><td>Manual Sort HC</td></tr>
                <tr><td><b>Transfer Out - Direct</b></td></tr>
                <tr><td>Manual Palletize HC</td></tr>
                <tr><td>Fluid Load (incl. Wall Builder) HC</td></tr>
                <tr><td><b>Transfer Out Dock - Direct</b></td></tr>
                <tr><td>Dock Pallet Loader HC</td></tr>
                <tr><td><b>Receive Dock</b></td></tr>
                <tr><td>Inbound Dock Clerk (RSVDC)</td></tr>
                <tr><td>Inbound Yard Driver (RSVIYD)</td></tr>
                <tr><td>PID Manual Divert (PIDMNDIV)</td></tr>
                <tr><td>PID Truck Unload (PIDTRUNL)</td></tr>
                <tr><td>Receive Dock Crew (RSVCRW)</td></tr>
                <tr><td>Receive Dock TDR (RSVTDR)</td></tr>
                <tr><td>Receive Line Loader (RSVLD)</td></tr>
                <tr><td>ReceiveLine Unloader (RSVULD)</td></tr>
                <tr><td>Vendor Cutter (VDRCUT)</td></tr>
                <tr><td>Vendor Line Load (VDRLRD)</td></tr>
                <tr><td><b>Receive-Support</b></td></tr>
                <tr><td>Case Rcv WaterSpider (CASEWATER)</td></tr>
                <tr><td>General Audits (GENAUDIT)</td></tr>
                <tr><td>Rcv WaterSpider (WATER)</td></tr>
                <tr><td>Receive 5S (RSV5S)</td></tr>
                <tr><td>MHE Support (MHERECS)</td></tr>
                <tr><td>Offline_Mods (OFFMODRS)</td></tr>
                <tr><td>IB Tote Replen (RSVRPL)</td></tr>
                <tr><td>PID Gatekeep (PIDGATEKEEP)</td></tr>
                <tr><td>Receive Ambassador (RAMB)</td></tr>
                <tr><td>Receive Dock Crew (RSDOCK)</td></tr>
                <tr><td>Receive Training (RSVTR)</td></tr>
                <tr><td><b>Transfer In Support</b></td></tr>
                <tr><td>TransferIn DockClerk (TITDC)</td></tr>
                <tr><td>Cart/Pallet Builder (PLTBLD)</td></tr>
                <tr><td>Line Load Injection (LINLNJT)</td></tr>
                <tr><td>TransferIn ToteStkng (TOTSTG)</td></tr>
                <tr><td>Cart Runner Trans (CRNTRA)</td></tr>
                <tr><td>Kermit Operator (KERMIT)</td></tr>
                <tr><td>Bin Scout Trans (BSCTRA)</td></tr>
                <tr><td>TransferIn Dock Crew (TRFICR)</td></tr>
                <tr><td>Trans Cart Run-Nike (NIKETRANSCART)</td></tr>
                <tr><td>Transfer In Ambssdr (TITA)</td></tr>
                <tr><td>Transfer In Training (TRFITR)</td></tr>
                <tr><td>Transfer In 5S (TRF5S)</td></tr>
                <tr><td><b>Prep Support</b></td></tr>
                <tr><td>Prep Ambassador (PREPAMB)</td></tr>
                <tr><td>Prep Kaizen (PRPKZN)</td></tr>
                <tr><td>Prep Omake (PRPOMK)</td></tr>
                <tr><td>Prep Training (PRPTR)</td></tr>
                <tr><td>Prep 5S (PRP5S)</td></tr>
                <tr><td><b>IB Problem Solve</b></td></tr>
                <tr><td>ATAC Problem Solve (ATACPS)</td></tr>
                <tr><td>Damage Processing (REBOX)</td></tr>
                <tr><td>Damages (DAMAGES)</td></tr>
                <tr><td>DecantProblemSolve (DCNTPS)</td></tr>
                <tr><td>DecantPsolveBacklog (DCNTPSBL)</td></tr>
                <tr><td>IB Sweeper (LPSWEEP)</td></tr>
                <tr><td>ISS Field Rep (ICVR)</td></tr>
                <tr><td>Receive ProblemSolve (IBPS)</td></tr>
                <tr><td>Stow Psolve Backlog (PSBKL)</td></tr>
                <tr><td>Stow to Prime Psolve (RECON)</td></tr>
                <tr><td>Prep Problem Solve (PREPPS)</td></tr>
                <tr><td><b>Dock Lead/PA</b></td></tr>
                <tr><td>Dock Lead/PA (LDOCK)</td></tr>
                <tr><td>Receive Lead/PA (RSLR)</td></tr>
                <tr><td><b>RC Sort</b></td></tr>
                <tr><td>AIS_5lb_Induct (AISOPSS)</td></tr>
                <tr><td>RC Sort 5S (RSRT5S)</td></tr>
                <tr><td>UIS 20lb Case Prep (UISCASEXL)</td></tr>
                <tr><td>UIS 20lb Psolve (UIS20PS)</td></tr>
                <tr><td>UIS 5lb Psolve (UIS5PS)</td></tr>
                <tr><td>UIS Case Prep (UISCASE)</td></tr>
                <tr><td>UIS SupUser 20lb (UIS20SU)</td></tr>
                <tr><td>UIS_5lb_ToteWrangle</td></tr>
                <tr><td>Water Spider (RCWS)</td></tr>
                <tr><td>RC Sort Ambassador (RCRSA)</td></tr>
                <tr><td>RC Sort Training (RSRTR)</td></tr>
                <tr><td><b>RC Presort</b></td></tr>
                <tr><td>RC Presort Cases HC (incl. DIVERTER)</td></tr>
                <tr><td><b>Transfer Out</b></td></tr>
                <tr><td>Robotic Water Spider (ROBWS)</td></tr>
                <tr><td>Robotics Operator (ROPER)</td></tr>
                <tr><td>Trans Out Overflow (OVRFLW)</td></tr>
                <tr><td>Transfer Out 5S (TRF5S)</td></tr>
                <tr><td>Water Spider (EOLWS)</td></tr>
                <tr><td>Offline_Mods (OFFMODXO)</td></tr>
                <tr><td>Robotic Problem Solve (ROBPS)</td></tr>
                <tr><td>Transfer Out Ambssdr (TOTOA)</td></tr>
                <tr><td>TransferOut Training (TRFOTR)</td></tr>
                <tr><td><b>Transfer Out Dock</b></td></tr>
                <tr><td>Shipping Clerk (SHPCL)</td></tr>
                <tr><td>TransferOut DockCrew (TRFOCR)</td></tr>
                <tr><td>Outbound Dock Crew (OUTCRW)</td></tr>
                <tr><td>Truck Loader (MTTL)</td></tr>
                <tr><td><b>Transfer Out Lead/PA</b></td></tr>
                <tr><td>RC Sort Lead/PA (RSRSL)</td></tr>
                <tr><td>Transfer Out Lead/PA</td></tr>
                <tr><td><b>Trans Out Prob Solve</b></td></tr>
                <tr><td>Fluid Load Sweep (FSWEEP)</td></tr>
                <tr><td>RC Sort ProblemSolve (PSRSPS)</td></tr>
                <tr><td>TransferOut Psolve (PSTOPS)</td></tr>
                <tr><td>Workflow (WRKFLOW)</td></tr>
                <tr><td><b>Each Receive</b></td></tr>
                <tr><td>Non-PID Conveyable (NPC) HC</td></tr>
                <tr><td>Each Receive Traditional HC</td></tr>
                <tr><td><b>LP Receive</b></td></tr>
                <tr><td>PrEditor Receive HC</td></tr>
                <tr><td><b>Pallet Receive NVF</b></td></tr>
                <tr><td>Pallet Receive HC</td></tr>
                <tr><td><b>Prep</b></td></tr>
                <tr><td>Prep Recorder Traditional HC</td></tr>
                <tr><td>Prep Pallet HC (incl. Prep Other)</td></tr>
                <tr><td>ATAC (Cubiscan) HC</td></tr>
                <tr><td><b>Totals</b></td></tr>
                </tbody>
            </table>
        `;
    } else if (view === "Rates") {
        viewContainer.innerHTML = `
            <table border="1" cellpadding="5" cellspacing="0" class="headcount-table">
            <thead>
                <tr>
                    <th>Line Item</th>
                    <th>Planned Input CPH</th>
                    <th>Actual Input CPH</th>
                    <th>Planned Output CPH</th>
                    <th>Actual Output CPH</th>
                    <th>Planned UPH</th>
                    <th>Actual UPH</th>
                </tr>
            </thead>
            <tbody>
            <tr><td><b>Inbound Transfer In (TI)</b></td></tr>
            <tr><td>Case Transfer In "98" HC</td></tr>
            <tr><td>Pallet Transfer In HC</td></tr>
            <tr><td><b>Decant</b></td></tr>
            <tr><td>Transfer In Decant HC</td></tr>
            <tr><td>Decant Non-TI HC</td></tr>
            <tr><td><b>RC Sort - Direct</b></td></tr>
            <tr><td>UIS 5lb Inductor HC</td></tr>
            <tr><td>UIS 20lb Inductor HC</td></tr>
            <tr><td>Manual Sort HC</td></tr>
            <tr><td><b>Transfer Out - Direct</b></td></tr>
            <tr><td>Manual Palletize HC</td></tr>
            <tr><td>Fluid Load (incl. Wall Builder) HC</td></tr>
            <tr><td><b>Transfer Out Dock - Direct</b></td></tr>
            <tr><td>Dock Pallet Loader HC</td></tr>
            <tr><td><b>Receive Dock</b></td></tr>
            <tr><td>Inbound Dock Clerk (RSVDC)</td></tr>
            <tr><td>Inbound Yard Driver (RSVIYD)</td></tr>
            <tr><td>PID Manual Divert (PIDMNDIV)</td></tr>
            <tr><td>PID Truck Unload (PIDTRUNL)</td></tr>
            <tr><td>Receive Dock Crew (RSVCRW)</td></tr>
            <tr><td>Receive Dock TDR (RSVTDR)</td></tr>
            <tr><td>Receive Line Loader (RSVLD)</td></tr>
            <tr><td>ReceiveLine Unloader (RSVULD)</td></tr>
            <tr><td>Vendor Cutter (VDRCUT)</td></tr>
            <tr><td>Vendor Line Load (VDRLRD)</td></tr>
            <tr><td><b>Receive-Support</b></td></tr>
            <tr><td>Case Rcv WaterSpider (CASEWATER)</td></tr>
            <tr><td>General Audits (GENAUDIT)</td></tr>
            <tr><td>Rcv WaterSpider (WATER)</td></tr>
            <tr><td>Receive 5S (RSV5S)</td></tr>
            <tr><td>MHE Support (MHERECS)</td></tr>
            <tr><td>Offline_Mods (OFFMODRS)</td></tr>
            <tr><td>IB Tote Replen (RSVRPL)</td></tr>
            <tr><td>PID Gatekeep (PIDGATEKEEP)</td></tr>
            <tr><td>Receive Ambassador (RAMB)</td></tr>
            <tr><td>Receive Dock Crew (RSDOCK)</td></tr>
            <tr><td>Receive Training (RSVTR)</td></tr>
            <tr><td><b>Transfer In Support</b></td></tr>
            <tr><td>TransferIn DockClerk (TITDC)</td></tr>
            <tr><td>Cart/Pallet Builder (PLTBLD)</td></tr>
            <tr><td>Line Load Injection (LINLNJT)</td></tr>
            <tr><td>TransferIn ToteStkng (TOTSTG)</td></tr>
            <tr><td>Cart Runner Trans (CRNTRA)</td></tr>
            <tr><td>Kermit Operator (KERMIT)</td></tr>
            <tr><td>Bin Scout Trans (BSCTRA)</td></tr>
            <tr><td>TransferIn Dock Crew (TRFICR)</td></tr>
            <tr><td>Trans Cart Run-Nike (NIKETRANSCART)</td></tr>
            <tr><td>Transfer In Ambssdr (TITA)</td></tr>
            <tr><td>Transfer In Training (TRFITR)</td></tr>
            <tr><td>Transfer In 5S (TRF5S)</td></tr>
            <tr><td><b>Prep Support</b></td></tr>
            <tr><td>Prep Ambassador (PREPAMB)</td></tr>
            <tr><td>Prep Kaizen (PRPKZN)</td></tr>
            <tr><td>Prep Omake (PRPOMK)</td></tr>
            <tr><td>Prep Training (PRPTR)</td></tr>
            <tr><td>Prep 5S (PRP5S)</td></tr>
            <tr><td><b>IB Problem Solve</b></td></tr>
            <tr><td>ATAC Problem Solve (ATACPS)</td></tr>
            <tr><td>Damage Processing (REBOX)</td></tr>
            <tr><td>Damages (DAMAGES)</td></tr>
            <tr><td>DecantProblemSolve (DCNTPS)</td></tr>
            <tr><td>DecantPsolveBacklog (DCNTPSBL)</td></tr>
            <tr><td>IB Sweeper (LPSWEEP)</td></tr>
            <tr><td>ISS Field Rep (ICVR)</td></tr>
            <tr><td>Receive ProblemSolve (IBPS)</td></tr>
            <tr><td>Stow Psolve Backlog (PSBKL)</td></tr>
            <tr><td>Stow to Prime Psolve (RECON)</td></tr>
            <tr><td>Prep Problem Solve (PREPPS)</td></tr>
            <tr><td><b>Dock Lead/PA</b></td></tr>
            <tr><td>Dock Lead/PA (LDOCK)</td></tr>
            <tr><td>Receive Lead/PA (RSLR)</td></tr>
            <tr><td><b>RC Sort</b></td></tr>
            <tr><td>AIS_5lb_Induct (AISOPSS)</td></tr>
            <tr><td>RC Sort 5S (RSRT5S)</td></tr>
            <tr><td>UIS 20lb Case Prep (UISCASEXL)</td></tr>
            <tr><td>UIS 20lb Psolve (UIS20PS)</td></tr>
            <tr><td>UIS 5lb Psolve (UIS5PS)</td></tr>
            <tr><td>UIS Case Prep (UISCASE)</td></tr>
            <tr><td>UIS SupUser 20lb (UIS20SU)</td></tr>
            <tr><td>UIS_5lb_ToteWrangle</td></tr>
            <tr><td>Water Spider (RCWS)</td></tr>
            <tr><td>RC Sort Ambassador (RCRSA)</td></tr>
            <tr><td>RC Sort Training (RSRTR)</td></tr>
            <tr><td><b>RC Presort</b></td></tr>
            <tr><td>RC Presort Cases HC (incl. DIVERTER)</td></tr>
            <tr><td><b>Transfer Out</b></td></tr>
            <tr><td>Robotic Water Spider (ROBWS)</td></tr>
            <tr><td>Robotics Operator (ROPER)</td></tr>
            <tr><td>Trans Out Overflow (OVRFLW)</td></tr>
            <tr><td>Transfer Out 5S (TRF5S)</td></tr>
            <tr><td>Water Spider (EOLWS)</td></tr>
            <tr><td>Offline_Mods (OFFMODXO)</td></tr>
            <tr><td>Robotic Problem Solve (ROBPS)</td></tr>
            <tr><td>Transfer Out Ambssdr (TOTOA)</td></tr>
            <tr><td>TransferOut Training (TRFOTR)</td></tr>
            <tr><td><b>Transfer Out Dock</b></td></tr>
            <tr><td>Shipping Clerk (SHPCL)</td></tr>
            <tr><td>TransferOut DockCrew (TRFOCR)</td></tr>
            <tr><td>Outbound Dock Crew (OUTCRW)</td></tr>
            <tr><td>Truck Loader (MTTL)</td></tr>
            <tr><td><b>Transfer Out Lead/PA</b></td></tr>
            <tr><td>RC Sort Lead/PA (RSRSL)</td></tr>
            <tr><td>Transfer Out Lead/PA</td></tr>
            <tr><td><b>Trans Out Prob Solve</b></td></tr>
            <tr><td>Fluid Load Sweep (FSWEEP)</td></tr>
            <tr><td>RC Sort ProblemSolve (PSRSPS)</td></tr>
            <tr><td>TransferOut Psolve (PSTOPS)</td></tr>
            <tr><td>Workflow (WRKFLOW)</td></tr>
            <tr><td><b>Each Receive</b></td></tr>
            <tr><td>Non-PID Conveyable (NPC) HC</td></tr>
            <tr><td>Each Receive Traditional HC</td></tr>
            <tr><td><b>LP Receive</b></td></tr>
            <tr><td>PrEditor Receive HC</td></tr>
            <tr><td><b>Pallet Receive NVF</b></td></tr>
            <tr><td>Pallet Receive HC</td></tr>
            <tr><td><b>Prep</b></td></tr>
            <tr><td>Prep Recorder Traditional HC</td></tr>
            <tr><td>Prep Pallet HC (incl. Prep Other)</td></tr>
            <tr><td>ATAC (Cubiscan) HC</td></tr>
            <tr><td><b>Totals</b></td></tr>
            </tbody>
        </table>
    `;
    } else if (view === "FPP"){
        viewContainer.innerHTML = `
        <table border="1" cellpadding="5" cellspacing="0" class="assumption-table">
            <thead>
                <tr>
                    <th>FPP Line Item</th>
                    <th>Planned FPP Value</th>
                    <th>Actual FPP Value</th>
                </tr>
            </thead>
            <tbody>
            <tr><td>PR CPP</td></tr>
            <tr><td>Divert:PC Ratio</td></tr>
            <tr><td>5# UPC In</td></tr>
            <tr><td>20# UPC In</td></tr>
            <tr><td>MS UPC In</td></tr>
            <tr><td>5# UPC Out</td></tr>
            <tr><td>20# UPC Out</td></tr>
            <tr><td>MS UPC Out</td></tr>
            <tr><td>NVF Decant Units per Case In</td></tr>
            <tr><td>TI Decant Units per Case In</td></tr>
            <tr><td>NVF Decant Units per Tote Out</td></tr>
            <tr><td>TI Decant Units per Tote Out</td></tr>
            <tr><td>Decant to Sort Unit Ratio</td></tr>
            <tr><td>% Decant Units TI</td></tr>
            <tr><td>% Decant Output Breaking to Sort</td></tr>
            <tr><td>% PID Cartons Breaking Eaches</td></tr>
            <tr><td>% PID Cartons Breaking Prep</td></tr>
            <tr><td>% FL OB Diverts</td></tr>
            <tr><td>% MP OB Diverts</td></tr>
            <tr><td>% Robots OB Diverts</td></tr>
            <tr><td>Diverts Created by PS per Shift</td></tr>
            <tr><td>Presort Cases per Shift</td></tr>
            <tr><td>CPP Robots</td></tr>
            <tr><td>CPP MP</td></tr>
            <!-- Add more rows here if necessary -->
            </tbody>
        </table>
    `;
    } else if (view === "TP") {
        viewContainer.innerHTML = `
            <table border="1" cellpadding="5" cellspacing="0" class="headcount-table">
                <thead>
                    <tr>
                        <th>Line Item</th>
                        <th>Planned Jobs Input</th>
                        <th>Actual Jobs Input</th>
                        <th>Planned Jobs Output</th>
                        <th>Actual Jobs Output</th>
                        <th>Planned Units</th>
                        <th>Actual Units</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td><b>Inbound Transfer In (TI)</b></td></tr>
                <tr><td>Case Transfer In "98" HC</td></tr>
                <tr><td>Pallet Transfer In HC</td></tr>
                <tr><td><b>Decant</b></td></tr>
                <tr><td>Transfer In Decant HC</td></tr>
                <tr><td>Decant Non-TI HC</td></tr>
                <tr><td><b>RC Sort - Direct</b></td></tr>
                <tr><td>UIS 5lb Inductor HC</td></tr>
                <tr><td>UIS 20lb Inductor HC</td></tr>
                <tr><td>Manual Sort HC</td></tr>
                <tr><td><b>Transfer Out - Direct</b></td></tr>
                <tr><td>Manual Palletize HC</td></tr>
                <tr><td>Fluid Load (incl. Wall Builder) HC</td></tr>
                <tr><td><b>Transfer Out Dock - Direct</b></td></tr>
                <tr><td>Dock Pallet Loader HC</td></tr>
                <tr><td><b>Receive Dock</b></td></tr>
                <tr><td>Inbound Dock Clerk (RSVDC)</td></tr>
                <tr><td>Inbound Yard Driver (RSVIYD)</td></tr>
                <tr><td>PID Manual Divert (PIDMNDIV)</td></tr>
                <tr><td>PID Truck Unload (PIDTRUNL)</td></tr>
                <tr><td>Receive Dock Crew (RSVCRW)</td></tr>
                <tr><td>Receive Dock TDR (RSVTDR)</td></tr>
                <tr><td>Receive Line Loader (RSVLD)</td></tr>
                <tr><td>ReceiveLine Unloader (RSVULD)</td></tr>
                <tr><td>Vendor Cutter (VDRCUT)</td></tr>
                <tr><td>Vendor Line Load (VDRLRD)</td></tr>
                <tr><td><b>Receive-Support</b></td></tr>
                <tr><td>Case Rcv WaterSpider (CASEWATER)</td></tr>
                <tr><td>General Audits (GENAUDIT)</td></tr>
                <tr><td>Rcv WaterSpider (WATER)</td></tr>
                <tr><td>Receive 5S (RSV5S)</td></tr>
                <tr><td>MHE Support (MHERECS)</td></tr>
                <tr><td>Offline_Mods (OFFMODRS)</td></tr>
                <tr><td>IB Tote Replen (RSVRPL)</td></tr>
                <tr><td>PID Gatekeep (PIDGATEKEEP)</td></tr>
                <tr><td>Receive Ambassador (RAMB)</td></tr>
                <tr><td>Receive Dock Crew (RSDOCK)</td></tr>
                <tr><td>Receive Training (RSVTR)</td></tr>
                <tr><td><b>Transfer In Support</b></td></tr>
                <tr><td>TransferIn DockClerk (TITDC)</td></tr>
                <tr><td>Cart/Pallet Builder (PLTBLD)</td></tr>
                <tr><td>Line Load Injection (LINLNJT)</td></tr>
                <tr><td>TransferIn ToteStkng (TOTSTG)</td></tr>
                <tr><td>Cart Runner Trans (CRNTRA)</td></tr>
                <tr><td>Kermit Operator (KERMIT)</td></tr>
                <tr><td>Bin Scout Trans (BSCTRA)</td></tr>
                <tr><td>TransferIn Dock Crew (TRFICR)</td></tr>
                <tr><td>Trans Cart Run-Nike (NIKETRANSCART)</td></tr>
                <tr><td>Transfer In Ambssdr (TITA)</td></tr>
                <tr><td>Transfer In Training (TRFITR)</td></tr>
                <tr><td>Transfer In 5S (TRF5S)</td></tr>
                <tr><td><b>Prep Support</b></td></tr>
                <tr><td>Prep Ambassador (PREPAMB)</td></tr>
                <tr><td>Prep Kaizen (PRPKZN)</td></tr>
                <tr><td>Prep Omake (PRPOMK)</td></tr>
                <tr><td>Prep Training (PRPTR)</td></tr>
                <tr><td>Prep 5S (PRP5S)</td></tr>
                <tr><td><b>IB Problem Solve</b></td></tr>
                <tr><td>ATAC Problem Solve (ATACPS)</td></tr>
                <tr><td>Damage Processing (REBOX)</td></tr>
                <tr><td>Damages (DAMAGES)</td></tr>
                <tr><td>DecantProblemSolve (DCNTPS)</td></tr>
                <tr><td>DecantPsolveBacklog (DCNTPSBL)</td></tr>
                <tr><td>IB Sweeper (LPSWEEP)</td></tr>
                <tr><td>ISS Field Rep (ICVR)</td></tr>
                <tr><td>Receive ProblemSolve (IBPS)</td></tr>
                <tr><td>Stow Psolve Backlog (PSBKL)</td></tr>
                <tr><td>Stow to Prime Psolve (RECON)</td></tr>
                <tr><td>Prep Problem Solve (PREPPS)</td></tr>
                <tr><td><b>Dock Lead/PA</b></td></tr>
                <tr><td>Dock Lead/PA (LDOCK)</td></tr>
                <tr><td>Receive Lead/PA (RSLR)</td></tr>
                <tr><td><b>RC Sort</b></td></tr>
                <tr><td>AIS_5lb_Induct (AISOPSS)</td></tr>
                <tr><td>RC Sort 5S (RSRT5S)</td></tr>
                <tr><td>UIS 20lb Case Prep (UISCASEXL)</td></tr>
                <tr><td>UIS 20lb Psolve (UIS20PS)</td></tr>
                <tr><td>UIS 5lb Psolve (UIS5PS)</td></tr>
                <tr><td>UIS Case Prep (UISCASE)</td></tr>
                <tr><td>UIS SupUser 20lb (UIS20SU)</td></tr>
                <tr><td>UIS_5lb_ToteWrangle</td></tr>
                <tr><td>Water Spider (RCWS)</td></tr>
                <tr><td>RC Sort Ambassador (RCRSA)</td></tr>
                <tr><td>RC Sort Training (RSRTR)</td></tr>
                <tr><td><b>RC Presort</b></td></tr>
                <tr><td>RC Presort Cases HC (incl. DIVERTER)</td></tr>
                <tr><td><b>Transfer Out</b></td></tr>
                <tr><td>Robotic Water Spider (ROBWS)</td></tr>
                <tr><td>Robotics Operator (ROPER)</td></tr>
                <tr><td>Trans Out Overflow (OVRFLW)</td></tr>
                <tr><td>Transfer Out 5S (TRF5S)</td></tr>
                <tr><td>Water Spider (EOLWS)</td></tr>
                <tr><td>Offline_Mods (OFFMODXO)</td></tr>
                <tr><td>Robotic Problem Solve (ROBPS)</td></tr>
                <tr><td>Transfer Out Ambssdr (TOTOA)</td></tr>
                <tr><td>TransferOut Training (TRFOTR)</td></tr>
                <tr><td><b>Transfer Out Dock</b></td></tr>
                <tr><td>Shipping Clerk (SHPCL)</td></tr>
                <tr><td>TransferOut DockCrew (TRFOCR)</td></tr>
                <tr><td>Outbound Dock Crew (OUTCRW)</td></tr>
                <tr><td>Truck Loader (MTTL)</td></tr>
                <tr><td><b>Transfer Out Lead/PA</b></td></tr>
                <tr><td>RC Sort Lead/PA (RSRSL)</td></tr>
                <tr><td>Transfer Out Lead/PA</td></tr>
                <tr><td><b>Trans Out Prob Solve</b></td></tr>
                <tr><td>Fluid Load Sweep (FSWEEP)</td></tr>
                <tr><td>RC Sort ProblemSolve (PSRSPS)</td></tr>
                <tr><td>TransferOut Psolve (PSTOPS)</td></tr>
                <tr><td>Workflow (WRKFLOW)</td></tr>
                <tr><td><b>Each Receive</b></td></tr>
                <tr><td>Non-PID Conveyable (NPC) HC</td></tr>
                <tr><td>Each Receive Traditional HC</td></tr>
                <tr><td><b>LP Receive</b></td></tr>
                <tr><td>PrEditor Receive HC</td></tr>
                <tr><td><b>Pallet Receive NVF</b></td></tr>
                <tr><td>Pallet Receive HC</td></tr>
                <tr><td><b>Prep</b></td></tr>
                <tr><td>Prep Recorder Traditional HC</td></tr>
                <tr><td>Prep Pallet HC (incl. Prep Other)</td></tr>
                <tr><td>ATAC (Cubiscan) HC</td></tr>
                <tr><td><b>Totals</b></td></tr>
                    <!-- Add more rows here based on the content from the table -->
                </tbody>
            </table>
            <table border="1" cellpadding="5" cellspacing="0" class="throughput-table">
                <thead>
                    <tr>
                        <th>Throughput Line Item</th>
                        <th>Planned Value</th>
                        <th>Actual Value</th>
                    </tr>
                </thead>
                <tbody>
                <tr><td>PID Cartons</td></tr>
                <tr><td>PR Pallets</td></tr>
                <tr><td>PR Cartons</td></tr>
                <tr><td>Combined Cartons</td></tr>
                <tr><td>Diverts</td></tr>
                <tr><td>CPLH w/o Support</td></tr>
                <tr><td>5# Units</td></tr>
                <tr><td>20# Units</td></tr>
                <tr><td>MS Units</td></tr>
                <tr><td>Total Sort Units</td></tr>
                </tbody>
            </table>
        `;
    }
}