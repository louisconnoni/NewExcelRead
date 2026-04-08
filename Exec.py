import matplotlib.pyplot as plt
import math as math
import numpy as np
import cmath as cmath
import pandas as pd
import numpy_financial as nf

## loading excel file
def load_input_data(excel_file): 
    
    inputdata = pd.read_excel(excel_file)
    columns = len(inputdata.columns)
    index = 1
    return inputdata, columns, index


def run_model(excel_file):
    """
    Entry point for the WHR model.
    """
    inputdata, columns, index = load_input_data(excel_file)

## Raza's Work

    op = inputdata.iloc[:, index]
    
    # INPUTS
    # Heat
    Q = op[2]#1e6  # waste heat transferred to CCS, watts
    HRE = op[18]#0.95
    wht = Q*HRE
    TDCin = op[3]#30  # DC WH fluid temperature at HX inlet in Celsius
    TDCout = op[4]#20  # DC WH fluid temperature at HX outlet in Celsius
    TOFFin = op[19]#18  # Offtaker inlet fluid temperature to absorb WH
    TOFFout = op[20]#28  # Offtaker outlet fluid temperature to absorb WH
    LMTDcor = op[21]#0.8  # LMTD correction factor for shell and tube
    U = op[22]#2500  # Heat transfer coefficient W/(m^2K)
    HXatov = op[23]#0.008  # rule of thumb material volume required per heat transfer area, shell and tube, not rigorous
    HXdensity = op[24]#2700  # kg/m^3
    HXppw = op[25]#3.25  # aluminum price per kg in dollars
    HXcpw = op[26]#15 * (1 / 907.2)  # tons CO2 per kg aluminum - carbon emissions per volume
    HXwpw = op[27]#14 * (1 / 907.2)  # m^3 H2O per kg aluminum - water usage per volume
    
    # Piping to Offtaker
    thickness = op[28]#0.6 / 100  # pipe thickness
    Rinner = op[29]#(20.32 / 100)/2  # pipe radius
    pipedensity = op[30]#950  # kg/m^3
    pipppw = op[31]#5.00  # hdpe price per kg in dollars
    pipcpw = op[32]#2.8 * (1 / 907.2)  # tons CO2 per kg piping - carbon emissions
    pipwpw = op[33]#0.005#8143 * 0.001 / 1000  # m^3 used per kg piping - water usage
    
    # to calculate radii required, will need to figure out flow rate and pressure drop - need physics model
    # heat transferred to offtaker is a function of flow rate, which is a function of fluid properties, pipe friction, pressure drop, inlet/outlet temperatures
    distance = op[34]#300  # distance offtaker is from datacenter in m
    
    #PHYSICS#
    #DC SIDE
    C_p = op[5]#3740 #30% propylene glycol mixture
    rho = op[6]#1030 #density
    mu = op[7]#2.48e-3 #dynamic viscosity
    ACS = np.pi*(Rinner**2) #pipe cross section
    mdot = Q/(C_p*(TDCin-TDCout)) #mass flow rate
    vel = mdot/(rho*ACS) #velocity
    Re = 2*rho*vel*Rinner/mu #Reynold's number
    friction = 0.316/(Re**0.25) #friction factor assuming smooth pipe
    deltap = (friction * 2* distance * rho * vel**2)/(2*Rinner*2) #pressure drop
    pumpeff = op[8]#0.6 #pump efficiency
    pumppower = 1.2 * deltap*vel*ACS/pumpeff #assumed 20% increase to account for heat exchanger pressure drop 
    
    # Offtaker
    sre = op[35]#2e9  # Specific regeneration energy, joules per ton CO2 (energy required to regenerate solvent)
    operatingpercent = op[36]#1#0.5  # percent of the time that the CCS plant is operating
    fuelemission = op[37]#0.202 * (1 / 907.2) * (1 / 1000)  # original heat source CO2 emission coefficient, tons per Wh
    fuelefficiency = op[38]#0.5
    fuelprice =  op[39]#3e-5#5e-5 # fuel price per Wh
    electricityprice = 5e-5
    #annual maintenance costs
    labor = 100000 #workers salary
    electricity = pumppower*24*365*electricityprice*2 #pump electricity, x2 assuming offtaker uses same pump power
    operation = 50000#taxes, permits, insurance
    maintenancecost = labor+electricity+operation  # will need to break this down and do a more refined calculation later
    # will be a function of distance, pump electricity, labor
    # yearly cost per MW thermal
    wateruse = op[41]#5 * (1 / 1.102)  # how much water the CCS uses per year - will need to break down further; m^3 per ton CO2 (originally metric ton)
    lifetime = round(op[42])#15  # how long the collaboration operates in years
    
    # Scoring weights
    Se = op[43]#0.25
    Sc = op[44]#0.25
    Sw = op[45]#0.25
    Ssocial = op[46]#0.25
    S1sub = op[47]#1/3
    S2sub = op[48]#1/3
    S3sub = op[49]#1/3
    S3water = op[50]#1/3
    S3food = op[51]#1/3
    S3heat = op[52]#1/3
    S4sub = op[61]#0
    
    # on a scale from 0 - 1, then average calculated for total social score
    jobs = op[53]#5
    jobsbaseline = op[54]#200
    social1 = ((jobs/jobsbaseline)*0.333)/0.333
    # economic production - jobs/services provided
    social2 = op[55]#(0.28)/0.333
    # catastrophe - max score if no chance of disaster, and/or if no community impact when disaster occurs
    social3water = op[56]#0
    social3food = op[57]#0
    social3DH = op[58]#0
    waterscarcity = op[13]#0.8 #aqueduct score divided by 5 
    foodscarcity = op[14]#2.5/60 #percent undernourishment divided by 60 (60% = 1)
    heatdemand = op[15]#1 - (303-218)/(308-218)#1 - (temp-243)/(313-243) K 
    heatprice = op[16]#0.05/0.46
    heatscarcity = heatdemand * heatprice
    social3 = S3water*social3water*waterscarcity+ S3food*social3food*foodscarcity + S3heat*social3DH*heatscarcity
    # equity - providing resources to communities in need (i.e. clean water, food)
    
    #lost opportunity = delays
    lostoperationtime = op[11]#0
    # accounting for the fact that initial expenditures could have been invested
    # elsewhere during this time to make a profit
    # includes potential advances or delays due to acceptance/rejection of the WHR technique by local community
    
    # metrics
    ITenergy = op[9]#4e6
    Totalenergy = op[10]#6e6
    heatrecov = wht/ITenergy
    #DCcarbon = 1e7 * (1 / 907.2)  # tons per year
    #DCwater = 1e4  # m^3 per year
    #CUE = DCcarbon / ITenergy
    #WUE = DCwater / ITenergy
    ERE = Totalenergy / ITenergy
    EREnew = (Totalenergy - wht) / ITenergy
    ERF = wht/Totalenergy
    
    #optional inputs
    social4 = op[60]#0 #fourth social metric
    CTB = op[62]#0 #carbon tax benefit
    carbonsales = op[63]#0 #how much of teh captured CO2 gets sold by the operator, if they are not storing it
    shippingemission = op[64]#0#carbon shipping emissions of the sold CO2, if it is not stored
    #technological readiness just means more delays
    #technological readiness, permits/agreements (community acceptance), delay in receiving income from offtaker
    techtime = op[65]#0
    acceptancetime = op[66]#0
    
    socialscore = S1sub*social1 + S2sub*social2 + S3sub*social3 + S4sub*social4
        
    lostopportunity = techtime + acceptancetime + lostoperationtime  # time from proposal to operation in years
    
    variables = np.array([Q, HRE, TDCin, TDCout, TOFFin, TOFFout, LMTDcor, U, HXatov, HXdensity, HXppw, HXcpw, HXwpw, thickness, Rinner, pipedensity, pipppw, pipcpw, pipwpw, distance, sre])
    sensitivities = np.zeros(len(variables))
    uncertainties = np.zeros(len(variables))
    
    # CALCULATIONS
    # preliminary
    # HX Weight
    if((TDCin - TOFFout) == (TDCout - TOFFin)):
        LMTD = TDCin - TOFFout
    else:
        LMTD = (((TDCin - TOFFout) - (TDCout - TOFFin)) / math.log((TDCin - TOFFout) / (TDCout - TOFFin))) * LMTDcor
    Area = wht / (U * LMTD)
    HXvolume = Area * HXatov
    HXweight = HXdensity * HXvolume
    
    # Pipe Weight
    pipevolume = (math.pi * (Rinner + thickness)**2 - math.pi * (Rinner)**2) * distance * 2  # times 2 to account for both delivery and return
    pipeweight = pipevolume * pipedensity
    
    # social
    totalsocial = socialscore
    
    # carbon
    # principal
    carbonprincipal = ((HXweight * HXcpw) + (pipeweight * pipcpw))
    carbonprincipal = 1.15 * carbonprincipal #installation
    carbonprincipal = 1.1 * carbonprincipal #engineering
    carbonprincipal = 1.1 * carbonprincipal #contingency
    #additional increases for machining, installation, transport
    
    # annual savings
    carbonremoved = wht * 60 * 60 * 24 * 365 * (1 / sre) * operatingpercent - (carbonsales+shippingemission)
    # tons CO2 per year removed, offtaker side
    carbonavoided = fuelemission * wht * 24 * 365 * operatingpercent/fuelefficiency
    # scope 2, could be 0 if already using renewable
    othercarbonemissions = 200 + electricity*fuelemission*operatingpercent
    # there will be other yearly carbon emissions that must be accounted for
    # such as pump electricity, maintenance and transportation footprints
    # offtaker side
    carbonsaved = carbonremoved + carbonavoided - othercarbonemissions
    bline0c = -othercarbonemissions
    bline1c = carbonremoved + carbonavoided
    # principal - need to add lifecycle analysis from laying down infrastructure to
    # transport heat to CCS operator - could solely include this and ignore CCS
    # plant carbon footprint?
    
    # carbonprincipal = 100 * (1/907.2) * carbonremoved # assuming flat rate
    # based on capacity - 100 kg CO2 principal per ton yearly capacity
    
    totalcarbonsaved = carbonsaved * lifetime - carbonprincipal  # tons CO2
    baseline0c = bline0c * lifetime - carbonprincipal
    baseline1c = bline1c * lifetime - carbonprincipal
    carbonnpvs = [totalcarbonsaved, baseline0c, baseline1c]
    cfc = [-carbonprincipal] + [carbonsaved]*lifetime
    rc = nf.irr(cfc)
    
    
    #economic
    
    #principal
    econprincipal = ((HXweight*HXppw) + (pipeweight*pipppw))
    econprincipal = 1.15 * econprincipal #installation
    econprincipal = 1.1 * econprincipal #engineering
    econprincipal = 1.1 * econprincipal #contingency
    #additional increases for machining, installation, transport
    #annual savings
    #need to add function of distance
    annualcosts = maintenancecost * (wht/1000000) #assuming flat rate based on capacity - actually more complicated
    #assuming 100k per MW thermal
    annualprofit = fuelprice * wht*24*365 * operatingpercent/fuelefficiency + CTB * carbonremoved#how much the heat is being sold for
    moneysaved = annualprofit-annualcosts
    bline0e = -annualcosts
    bline1e = annualprofit
    #salvage
    salvage = 0.2 * econprincipal #assume 20% salvage
    
    totalprofit = moneysaved*(lifetime-lostopportunity) + salvage - econprincipal
    baseline0e = bline0e*(lifetime-lostopportunity) + salvage - econprincipal
    baseline1e = bline1e*(lifetime-lostopportunity) + salvage - econprincipal
    econnpvs = [totalprofit, baseline0e, baseline1e]
    cfe = [-econprincipal] + [moneysaved]*math.ceil(lifetime-lostopportunity)
    cfe[-1] += salvage
    re = nf.irr(cfe)
    #dollars
    
    #water
    
    #principal
    waterprincipal = ((HXweight*HXwpw) + (pipeweight*pipwpw)) 
    waterprincipal = 1.15 * waterprincipal #installation
    waterprincipal = 1.1 * waterprincipal #engineering
    waterprincipal = 1.1 * waterprincipal #contingency
    #additional increases for machining, installation, transport
    #annualsavings
    annualwaterusage =  wateruse * carbonremoved #offtaker side
    annualwaterproduction = 0 #CCS does not produce water
    annualwateravoidance = 1000 #Scope 2 - will have to calculate based on how much water fossil fuels use - subtract scope 2 electricity used for pumps
    watersaved = annualwaterproduction + annualwateravoidance - annualwaterusage
    bline0w = -annualwaterusage
    bline1w = annualwaterproduction + annualwateravoidance
    
    totalwatersaved = watersaved*lifetime - waterprincipal #m^3
    baseline0w = bline0w*lifetime - waterprincipal #m^3
    baseline1w = bline1w*lifetime - waterprincipal #m^3
    waternpvs = [totalwatersaved, baseline0w, baseline1w]
    cfw = [-waterprincipal] + [watersaved]*lifetime
    rw = nf.irr(cfw)
    
    carbonscore = (totalcarbonsaved - min(carbonnpvs))/(max(carbonnpvs)-min(carbonnpvs))
    econscore = (totalprofit - min(econnpvs))/(max(econnpvs)- min(econnpvs))
    waterscore = (totalwatersaved - min(waternpvs))/(max(waternpvs)- min(waternpvs))
    
    totalscore = Sc * carbonscore + Se * econscore + Sw * waterscore + Ssocial * socialscore
    
    EREchange = EREnew - ERE
    EREpercent = EREchange*100/ERE
    
  
    
    #sensitivity and uncertainty 
    counter = 0
    
    while(counter<len(variables)):
        if(counter > 0):
            variables[counter-1] = variables[counter-1]/1.01
        variables[counter] = variables[counter] * 1.01
        Q = variables[0]
        HRE = variables[1]
        TDCin = variables[2]
        TDCout = variables[3]
        TOFFin = variables[4]
        TOFFout = variables[5]
        LMTDcor = variables[6]
        U = variables[7] 
        HXatov = variables[8] 
        HXdensity = variables[9]
        HXppw = variables[10] 
        HXcpw = variables[11]
        HXwpw = variables[12]
        thickness = variables[13]
        Rinner = variables[14]
        pipedensity = variables[15] 
        pipppw = variables[16]
        pipcpw = variables[17]
        pipwpw = variables[18]
        distance = variables[19]
        sre = variables[20]
        
        wht = Q*HRE
        ACS = np.pi*(Rinner**2) #pipe cross section
        mdot = Q/(C_p*(TDCin-TDCout)) #mass flow rate
        vel = mdot/(rho*ACS) #velocity
        Re = 2*rho*vel*Rinner/mu #Reynold's number
        friction = 0.316/(Re**0.25) #friction factor assuming smooth pipe
        deltap = (friction * 2* distance * rho * vel**2)/(2*Rinner*2) #pressure drop
        pumppower = 1.2 * deltap*vel*ACS/pumpeff #assumed 20% increase to account for heat exchanger pressure drop 
        electricity = pumppower*24*365*electricityprice*2 #pump electricity, x2 assuming offtaker uses same pump power
        maintenancecost = labor+electricity+operation  # will need to break this down and do a more refined calculation later
        social1 = ((jobs/jobsbaseline)*0.333)/0.333
        heatscarcity = heatdemand * heatprice
        social3 = S3water*social3water*waterscarcity+ S3food*social3food*foodscarcity + S3heat*social3DH*heatscarcity
        heatrecov = wht/ITenergy
        ERE = Totalenergy / ITenergy
        EREnew = (Totalenergy - wht) / ITenergy
        ERF = wht/Totalenergy
        socialscore = S1sub*social1 + S2sub*social2 + S3sub*social3 + S4sub*social4
        lostopportunity = techtime + acceptancetime + lostoperationtime  # time from proposal to operation in years
        if((TDCin - TOFFout) == (TDCout - TOFFin)):
            LMTD = TDCin - TOFFout
        else:
            LMTD = (((TDCin - TOFFout) - (TDCout - TOFFin)) / math.log((TDCin - TOFFout) / (TDCout - TOFFin))) * LMTDcor
        Area = wht / (U * LMTD)
        HXvolume = Area * HXatov
        HXweight = HXdensity * HXvolume
    
        # Pipe Weight
        pipevolume = (math.pi * (Rinner + thickness)**2 - math.pi * (Rinner)**2) * distance * 2  # times 2 to account for both delivery and return
        pipeweight = pipevolume * pipedensity
    
        # social
        totalsocial = socialscore
    
        # carbon
        # principal
        carbonprincipal = ((HXweight * HXcpw) + (pipeweight * pipcpw))
        carbonprincipal = 1.15 * carbonprincipal #installation
        carbonprincipal = 1.1 * carbonprincipal #engineering
        carbonprincipal = 1.1 * carbonprincipal #contingency
        #additional increases for machining, installation, transport
    
        # annual savings
        carbonremoved = wht * 60 * 60 * 24 * 365 * (1 / sre) * operatingpercent - (carbonsales+shippingemission)
        # tons CO2 per year removed, offtaker side
        carbonavoided = fuelemission * wht * 24 * 365 * operatingpercent/fuelefficiency
        # scope 2, could be 0 if already using renewable
        othercarbonemissions = 200 + electricity*fuelemission*operatingpercent
        # there will be other yearly carbon emissions that must be accounted for
        # such as pump electricity, maintenance and transportation footprints
        # offtaker side
        carbonsaved = carbonremoved + carbonavoided - othercarbonemissions
        bline0c = -othercarbonemissions
        bline1c = carbonremoved + carbonavoided
        # principal - need to add lifecycle analysis from laying down infrastructure to
        # transport heat to CCS operator - could solely include this and ignore CCS
        # plant carbon footprint?
    
        # carbonprincipal = 100 * (1/907.2) * carbonremoved # assuming flat rate
        # based on capacity - 100 kg CO2 principal per ton yearly capacity
    
        totalcarbonsaved = carbonsaved * lifetime - carbonprincipal  # tons CO2
        baseline0c = bline0c * lifetime - carbonprincipal
        baseline1c = bline1c * lifetime - carbonprincipal
        carbonnpvs = [totalcarbonsaved, baseline0c, baseline1c]
        cfc = [-carbonprincipal] + [carbonsaved]*lifetime
        rc = nf.irr(cfc)
    
    
        #economic
    
        #principal
        econprincipal = ((HXweight*HXppw) + (pipeweight*pipppw))
        econprincipal = 1.15 * econprincipal #installation
        econprincipal = 1.1 * econprincipal #engineering
        econprincipal = 1.1 * econprincipal #contingency
        #additional increases for machining, installation, transport
        #annual savings
        #need to add function of distance
        annualcosts = maintenancecost * (wht/1000000) #assuming flat rate based on capacity - actually more complicated
        #assuming 100k per MW thermal
        annualprofit = fuelprice * wht*24*365 * operatingpercent/fuelefficiency + CTB * carbonremoved#how much the heat is being sold for
        moneysaved = annualprofit-annualcosts
        bline0e = -annualcosts
        bline1e = annualprofit
        #salvage
        salvage = 0.2 * econprincipal #assume 20% salvage
    
        totalprofit = moneysaved*(lifetime-lostopportunity) + salvage - econprincipal
        baseline0e = bline0e*(lifetime-lostopportunity) + salvage - econprincipal
        baseline1e = bline1e*(lifetime-lostopportunity) + salvage - econprincipal
        econnpvs = [totalprofit, baseline0e, baseline1e]
        cfe = [-econprincipal] + [moneysaved]*math.ceil(lifetime-lostopportunity)
        cfe[-1] += salvage
        re = nf.irr(cfe)
        #dollars
    
        #water
    
        #principal
        waterprincipal = ((HXweight*HXwpw) + (pipeweight*pipwpw)) 
        waterprincipal = 1.15 * waterprincipal #installation
        waterprincipal = 1.1 * waterprincipal #engineering
        waterprincipal = 1.1 * waterprincipal #contingency
        #additional increases for machining, installation, transport
        #annualsavings
        annualwaterusage =  wateruse * carbonremoved #offtaker side
        annualwaterproduction = 0 #CCS does not produce water
        annualwateravoidance = 1000 #Scope 2 - will have to calculate based on how much water fossil fuels use - subtract scope 2 electricity used for pumps
        watersaved = annualwaterproduction + annualwateravoidance - annualwaterusage
        bline0w = -annualwaterusage
        bline1w = annualwaterproduction + annualwateravoidance
    
        totalwatersaved = watersaved*lifetime - waterprincipal #m^3
        baseline0w = bline0w*lifetime - waterprincipal #m^3
        baseline1w = bline1w*lifetime - waterprincipal #m^3
        waternpvs = [totalwatersaved, baseline0w, baseline1w]
        cfw = [-waterprincipal] + [watersaved]*lifetime
        rw = nf.irr(cfw)
    
        carbonscore = (totalcarbonsaved - min(carbonnpvs))/(max(carbonnpvs)-min(carbonnpvs))
        econscore = (totalprofit - min(econnpvs))/(max(econnpvs)- min(econnpvs))
        waterscore = (totalwatersaved - min(waternpvs))/(max(waternpvs)- min(waternpvs))
    
        totalscore2 = Sc * carbonscore + Se * econscore + Sw * waterscore + Ssocial * socialscore
    
        EREchange = EREnew - ERE
        EREpercent = EREchange*100/ERE
        sensitivities[counter] = (totalscore2-totalscore)/(0.01*(variables[counter]/1.01))
        uncertainties[counter] = sensitivities[counter] * 0.1 * variables[counter]/1.01
        counter = counter + 1
        
    
    categories = ['Total Score', 'Carbon Score', 'Economic Score', 'Water Score', 'Social Score']
    values = [totalscore, carbonscore, econscore, waterscore, socialscore]
    # Define symmetric error values for each bar
    errors = [abs(np.linalg.norm(uncertainties)), 0, 0, 0, 0]





    
    # PACKAGE FINAL RESULTS
    
    
    ERE_improvement = EREpercent * -1
    
    results = {
        "Total Profit": totalprofit,
        "Total Water Saved": totalwatersaved,
        "Total Carbon Saved": totalcarbonsaved,
        "Total Score": totalscore,
        "Water Score": waterscore,
        "Economic Score": econscore,
        "Social Score": socialscore,
        "Carbon Score": carbonscore,
        "ERE Improvement": ERE_improvement,
        "ERF": erf
    }

return results

    while index < columns:
        print(
            "DISCLAIMER: Calculations are dependent upon assumptions described in manual"
        )
        index += 1

    return inputdata
