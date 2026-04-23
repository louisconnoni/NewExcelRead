
import matplotlib.pyplot as plt
import math as math
import numpy as np
import cmath as cmath
import pandas as pd
import numpy_financial as nf

# model.py

import numpy as np
import math
import numpy_financial as nf


def run_model_for_column(op):

 #-
 ## Razas portions
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
 weightpermeter = (np.pi*(Rinner+thickness)**2 - np.pi*(Rinner)**2)*pipedensity
 # to calculate radii required, will need to figure out flow rate and pressure drop - need physics model
 # heat transferred to offtaker is a function of flow rate, which is a function of fluid properties, pipe friction, pressure drop, inlet/outlet temperatures
 distance = op[34]#300  # distance offtaker is from datacenter in m

 #PHYSICS#
 #DC - OFFTAKER CONNECTION
 C_p = op[5]#3740 #specific heat 30% propylene glycol mixture
 rho = op[6]#1030 #density
 mu = op[7]#2.48e-3 #dynamic viscosity
 ACS = np.pi*(Rinner**2) #pipe cross section
 mdot = wht/(C_p*(TOFFout-TOFFin)) #mass flow rate
 vel = mdot/(rho*ACS) #velocity
 Re = 2*rho*vel*Rinner/mu #Reynold's number
 friction = 0.316/(Re**0.25) #friction factor assuming smooth pipe
 deltap = (friction * 2* distance * rho * vel**2)/(2*Rinner*2) + 68947.6#pressure drop, add 10psi drop for HX
 pumpeff = op[8]#0.6 #pump efficiency
 pumppower = deltap*vel*ACS/pumpeff #pump power calculated from pressure drop
 soiltemp = op[61] #18 temperature of soil surrounding piping
 L_c = op[62] #2000 characteristic distance
 whtnet = wht - mdot*C_p*(TOFFout - (soiltemp+(TOFFout-soiltemp)*np.exp(-distance/L_c))) #accounting for heat lost to ground during transmission
 
 
 # Offtaker
 Vw = op[35]#sre = op[35]#2e9  # Specific regeneration energy, joules per ton CO2 (energy required to regenerate solvent)
 operatingpercent = op[36]#1#0.5  # percent of the time that the CCS plant is operating
 fuelemission = op[37]#0.202 * (1 / 907.2) * (1 / 1000)  # original heat source CO2 emission coefficient, tons per Wh
 fuelefficiency = op[38]#0.5
 fuelprice =  op[39]#3e-5#5e-5 # fuel price per Wh
 electricityprice = op[40]#5e-5
 #annual maintenance costs
 labor = op[41]#100000 #workers salary
 electricity = pumppower*24*365*electricityprice #pump electricity cost
 electricenergy = pumppower*24*365 #pump electricity energy
 operation = op[42]#50000#taxes, permits, insurance
 maintenancecost = labor+operation  # will need to break this down and do a more refined calculation later
 # will be a function of distance, pump electricity, labor
 # yearly cost per MW thermal
 carbonem = op[43]#5 * (1 / 1.102)  # how much water the CCS uses per year - will need to break down further; m^3 per ton CO2 (originally metric ton)
 ewif = op[63] # 9.2e-7 water usage of replaced power plant
 lifetime = round(op[44])#15  # how long the collaboration operates in years
 
 # Scoring weights
 Se = op[45]#0.25
 Sc = op[46]#0.25
 Sw = op[47]#0.25
 Ssocial = op[48]#0.25
 S1sub = op[49]#1/3
 S2sub = op[50]#1/3
 S3sub = op[51]#1/3
 S3water = op[52]#1/3
 S3food = op[53]#1/3
 S3heat = op[54]#1/3
 S4sub = op[66]#0
 
 # on a scale from 0 - 1, then average calculated for total social score
 jobs = op[55]#5
 jobsbaseline = op[56]#200
 social1 = ((jobs/jobsbaseline)*0.333)/0.333
 # economic production - jobs/services provided
 social2 = op[57]#(0.28)/0.333
 # catastrophe - max score if no chance of disaster, and/or if no community impact when disaster occurs
 social3water = op[58]#0
 social3food = op[59]#0
 social3DH = op[60]#0
 waterscarcity = op[13]#0.8 #aqueduct score divided by 5 
 foodscarcity = op[14]#2.5/60 #percent undernourishment divided by 60 (60% = 1)
 heatdemand = op[15]#(x-500)/(12600-500)#1 - (303-218)/(308-218)#1 - (temp-243)/(313-243) K 
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
 social4 = op[65]#0 #fourth social metric
 CTB = op[67]#0 #carbon tax benefit
 carbonsales = op[68]#0 #how much of teh captured CO2 gets sold by the operator, if they are not storing it
 shippingemission = op[69]#0#carbon shipping emissions of the sold CO2, if it is not stored
 #technological readiness just means more delays
 #technological readiness, permits/agreements (community acceptance), delay in receiving income from offtaker
 techtime = op[70]#0
 acceptancetime = op[71]#0
 transport_price = op[72]
 transport_carbon = op[73]
 transport_water = op[74]
 
 socialscore = S1sub*social1 + S2sub*social2 + S3sub*social3 + S4sub*social4
     
 lostopportunity = techtime + acceptancetime + lostoperationtime  # time from proposal to operation in years
 
 variables = np.array([Q, HRE, TDCin, TDCout, TOFFin, TOFFout, LMTDcor, U, HXatov, HXdensity, HXppw, HXcpw, HXwpw, thickness, Rinner, pipedensity, pipppw, pipcpw, pipwpw, distance, C_p, rho, mu, pumpeff, Vw, operatingpercent, fuelemission, fuelefficiency, fuelprice, electricityprice, labor, operation, carbonem, Se, Sc, Sw, Ssocial, S1sub, S2sub, S3sub, S3water, S3food, S3heat, S4sub, jobs, jobsbaseline, social2, social3water, social3food, social3DH, waterscarcity, foodscarcity, heatdemand, heatprice, lostoperationtime, ITenergy, Totalenergy, social4, CTB, carbonsales, shippingemission, techtime, acceptancetime, transport_price, transport_carbon, transport_water, soiltemp, L_c, ewif])
 sensitivities = np.zeros(len(variables))
 uncertainties = np.zeros(len(variables))
 sensitivitieswater = np.zeros(len(variables))
 uncertaintieswater = np.zeros(len(variables))
 sensitivitiescarbon = np.zeros(len(variables))
 uncertaintiescarbon = np.zeros(len(variables))
 sensitivitiesecon = np.zeros(len(variables))
 uncertaintiesecon = np.zeros(len(variables))
 sensitivitiessocial = np.zeros(len(variables))
 uncertaintiessocial = np.zeros(len(variables))
 
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
 
 #water
 
 #principal
 #HX + pipe + transport + pump
 waterprincipal = 6.57*(wht/1000)+119.33+ (1.21*weightpermeter + 0.001)*2*distance + transport_water + 0.025*pumppower + 3.38#((HXweight*HXwpw) + (pipeweight*pipwpw)) + transport_water
 waterprincipal = 1.15 * waterprincipal #installation
 waterprincipal = 1.1 * waterprincipal #engineering
 waterprincipal = 1.1 * waterprincipal #contingency
 #additional increases for machining, installation, transport
 #annualsavings
 annualwaterusage =  electricenergy*ewif*operatingpercent#pumping water to homes may have scope 2 water
 annualwaterproduction = Vw * whtnet * 24 * 365 * operatingpercent
 annualwateravoidance = ewif*whtnet * 24 * 365 * operatingpercent/fuelefficiency #1000 #Scope 2 - will have to calculate based on how much water fossil fuels use - subtract scope 2 electricity used for pumps
 watersaved = annualwaterproduction + annualwateravoidance - annualwaterusage
 bline0w = -annualwaterusage
 bline1w = annualwaterproduction + annualwateravoidance
 
 totalwatersaved = watersaved*lifetime - waterprincipal #m^3
 baseline0w = bline0w*lifetime - waterprincipal #m^3
 baseline1w = bline1w*lifetime - waterprincipal #m^3
 waternpvs = [totalwatersaved, baseline0w, baseline1w]
 cfw = [-waterprincipal] + [watersaved]*lifetime
 rw = nf.irr(cfw)
 
 
 # carbon
 # principal
 #HX + pipe + transport + pump
 carbonprincipal = 16.52*(wht/1000)+348 + 3.787*weightpermeter*2*distance + transport_carbon + 0.057*pumppower + 6.82#((HXweight * HXcpw) + (pipeweight * pipcpw)) + transport_carbon
 carbonprincipal = 1.15 * carbonprincipal #installation
 carbonprincipal = 1.1 * carbonprincipal #engineering
 carbonprincipal = 1.1 * carbonprincipal #contingency
 #additional increases for machining, installation, transport
 
 # annual savings
 carbonremoved = 0#pumping water to homes may have carbon emissions
 # tons CO2 per year removed, offtaker side
 carbonavoided = fuelemission * whtnet * 24 * 365 * operatingpercent/fuelefficiency
 # scope 2, could be 0 if already using renewable
 othercarbonemissions = carbonem * annualwaterproduction + electricenergy*fuelemission*operatingpercent
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
 econprincipal = 300*(wht/100000)**0.6 + ((pipeweight*pipppw)) + transport_price + 100*(pumppower/373)**0.8#econprincipal = ((HXweight*HXppw) + (pipeweight*pipppw)) + transport_price
 econprincipal = 1.15 * econprincipal #installation
 econprincipal = 1.1 * econprincipal #engineering
 econprincipal = 1.1 * econprincipal #contingency
 #additional increases for machining, installation, transport
 #annual savings
 #need to add function of distance
 annualcosts = maintenancecost * (wht/1000000) + electricity#assuming flat rate based on capacity - actually more complicated
 #assuming 100k per MW thermal
 annualprofit = fuelprice * whtnet*24*365 * operatingpercent/fuelefficiency #how much the heat is being sold for
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
 
 
 carbonscore = (totalcarbonsaved - min(carbonnpvs))/(max(carbonnpvs)-min(carbonnpvs))
 econscore = (totalprofit - min(econnpvs))/(max(econnpvs)- min(econnpvs))
 waterscore = (totalwatersaved - min(waternpvs))/(max(waternpvs)- min(waternpvs))
 
 totalscore = Sc * carbonscore + Se * econscore + Sw * waterscore + Ssocial * socialscore
 
 EREchange = EREnew - ERE
 EREpercent = EREchange*100/ERE
 
 waterscore1 = waterscore
 carbonscore1 = carbonscore
 econscore1 = econscore
 socialscore1 = socialscore
 
 
 
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
     C_p = variables[20] 
     rho = variables[21]
     mu = variables[22]
     pumpeff = variables[23]
     Vw = variables[24]
     operatingpercent = variables[25]
     fuelemission = variables[26]
     fuelefficiency = variables[27]
     fuelprice = variables[28]
     electricityprice = variables[29]
     labor = variables[30]
     operation = variables[31]
     carbonem = variables[32]
     Se = variables[33]
     Sc = variables[34]
     Sw = variables[35]
     Ssocial = variables[36]
     S1sub = variables[37]
     S2sub = variables[38]
     S3sub = variables[39]
     S3water = variables[40]
     S3food = variables[41]
     S3heat = variables[42]
     S4sub = variables[43] 
     jobs = variables[44]
     jobsbaseline = variables[45]
     social2 = variables[46]
     social3water = variables[47]
     social3food = variables[48]
     social3DH = variables[49]
     waterscarcity = variables[50]
     foodscarcity = variables[51]
     heatdemand = variables[52]
     heatprice = variables[53]
     lostoperationtime = variables[54]
     ITenergy = variables[55]
     Totalenergy = variables[56]
     social4 = variables[57]
     CTB = variables[58]
     carbonsales = variables[59]
     shippingemission = variables[60]
     techtime = variables[61]
     acceptancetime = variables[62]
     transport_price = variables[63]
     transport_carbon = variables[64]
     transport_water = variables[65]
     soiltemp = variables[66]
     L_c = variables[67]
     ewif = variables[68]
     
     wht = Q*HRE
     weightpermeter = (np.pi*(Rinner+thickness)**2 - np.pi*(Rinner)**2)*pipedensity
     ACS = np.pi*(Rinner**2) #pipe cross section
     mdot = wht/(C_p*(TOFFout-TOFFin)) #mass flow rate
     vel = mdot/(rho*ACS) #velocity
     Re = 2*rho*vel*Rinner/mu #Reynold's number
     friction = 0.316/(Re**0.25) #friction factor assuming smooth pipe
     deltap = (friction * 2* distance * rho * vel**2)/(2*Rinner*2) + 68947.6#pressure drop, add 10psi drop for HX
     pumppower = deltap*vel*ACS/pumpeff 
     whtnet = wht - mdot*C_p*(TOFFout - (soiltemp+(TOFFout-soiltemp)*np.exp(-distance/L_c))) #accounting for heat lost to ground during transmission
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
     
     #water
 
     #principal
     waterprincipal = 6.57*(wht/1000)+119.33+ (1.21*weightpermeter + 0.001)*2*distance + transport_water + 0.025*pumppower + 3.38#((HXweight*HXwpw) + (pipeweight*pipwpw)) + transport_water
     waterprincipal = 1.15 * waterprincipal #installation
     waterprincipal = 1.1 * waterprincipal #engineering
     waterprincipal = 1.1 * waterprincipal #contingency
     #additional increases for machining, installation, transport
     #annualsavings
     annualwaterusage =  electricenergy*ewif*operatingpercent#offtaker side
     annualwaterproduction = Vw * whtnet * 24 * 365 * operatingpercent
     annualwateravoidance = ewif * whtnet * 24 * 365 * operatingpercent/fuelefficiency #1000 #Scope 2 - will have to calculate based on how much water fossil fuels use - subtract scope 2 electricity used for pumps
     watersaved = annualwaterproduction + annualwateravoidance - annualwaterusage
     bline0w = -annualwaterusage
     bline1w = annualwaterproduction + annualwateravoidance
 
     totalwatersaved = watersaved*lifetime - waterprincipal #m^3
     baseline0w = bline0w*lifetime - waterprincipal #m^3
     baseline1w = bline1w*lifetime - waterprincipal #m^3
     waternpvs = [totalwatersaved, baseline0w, baseline1w]
     cfw = [-waterprincipal] + [watersaved]*lifetime
     rw = nf.irr(cfw)
 
     # carbon
     # principal
     carbonprincipal = 16.52*(wht/1000)+348 + 3.787*weightpermeter*2*distance + transport_carbon + 0.057*pumppower + 6.82#((HXweight * HXcpw) + (pipeweight * pipcpw)) + transport_carbon
     carbonprincipal = 1.15 * carbonprincipal #installation
     carbonprincipal = 1.1 * carbonprincipal #engineering
     carbonprincipal = 1.1 * carbonprincipal #contingency
     #additional increases for machining, installation, transport
 
     # annual savings
     carbonremoved = 0
     # tons CO2 per year removed, offtaker side
     carbonavoided = fuelemission * whtnet * 24 * 365 * operatingpercent/fuelefficiency
     # scope 2, could be 0 if already using renewable
     othercarbonemissions = carbonem * annualwaterproduction + electricenergy*fuelemission*operatingpercent
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
     econprincipal = 300*(wht/100000)**0.6 + ((pipeweight*pipppw)) + transport_price + 100*(pumppower/373)**0.8#econprincipal = ((HXweight*HXppw) + (pipeweight*pipppw)) + transport_price
     econprincipal = 1.15 * econprincipal #installation
     econprincipal = 1.1 * econprincipal #engineering
     econprincipal = 1.1 * econprincipal #contingency
     #additional increases for machining, installation, transport
     #annual savings
     #need to add function of distance
     annualcosts = maintenancecost * (wht/1000000) + electricity#assuming flat rate based on capacity - actually more complicated
     #assuming 100k per MW thermal
     annualprofit = fuelprice * whtnet*24*365 * operatingpercent/fuelefficiency#how much the heat is being sold for
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
 
     carbonscore = (totalcarbonsaved - min(carbonnpvs))/(max(carbonnpvs)-min(carbonnpvs))
     econscore = (totalprofit - min(econnpvs))/(max(econnpvs)- min(econnpvs))
     waterscore = (totalwatersaved - min(waternpvs))/(max(waternpvs)- min(waternpvs))
 
     totalscore2 = Sc * carbonscore + Se * econscore + Sw * waterscore + Ssocial * socialscore
 
     EREchange = EREnew - ERE
     EREpercent = EREchange*100/ERE
     sensitivities[counter] = (totalscore2-totalscore)/(0.01*(variables[counter]/1.01))
     uncertainties[counter] = abs(sensitivities[counter] * 0.1 * variables[counter]/1.01)
     sensitivitieswater[counter] = (waterscore-waterscore1)/(0.01*(variables[counter]/1.01))
     uncertaintieswater[counter] = abs(sensitivitieswater[counter] * 0.1 * variables[counter]/1.01)
     sensitivitiescarbon[counter] = (carbonscore-carbonscore1)/(0.01*(variables[counter]/1.01))
     uncertaintiescarbon[counter] = abs(sensitivitiescarbon[counter] * 0.1 * variables[counter]/1.01)
     sensitivitiesecon[counter] = (econscore-econscore1)/(0.01*(variables[counter]/1.01))
     uncertaintiesecon[counter] = abs(sensitivitiesecon[counter] * 0.1 * variables[counter]/1.01)
     sensitivitiessocial[counter] = (socialscore-socialscore1)/(0.01*(variables[counter]/1.01))
     uncertaintiessocial[counter] = abs(sensitivitiessocial[counter] * 0.1 * variables[counter]/1.01)
     
     counter = counter + 1

 
 categories = ['Total Score', 'Carbon Score', 'Economic Score', 'Water Score', 'Social Score']
 values = [totalscore, carbonscore, econscore, waterscore, socialscore]
 # Define symmetric error values for each bar
 errors = [abs(np.linalg.norm(uncertainties)), abs(np.linalg.norm(uncertaintiescarbon)), abs(np.linalg.norm(uncertaintiesecon)), abs(np.linalg.norm(uncertaintieswater)), abs(np.linalg.norm(uncertaintiessocial))]


 

 return {
  "Total Profit": totalprofit,
  "Total Carbon Saved": totalcarbonsaved,
  "Total Water Saved": totalwatersaved,
  "Total Score" : totalscore,
  "Carbon Score": carbonscore,
  "Water Score": waterscore,
  "Economic Score": econscore,
  "Social Score": socialscore,
  "ERE improvement": EREpercent*-1,
  "ERF" : ERF,
  "Error": errors[0],
  "Economic Weight":Se,
  "Water Weight":Sw,
  "Carbon Weight":Sc,
  "Social Weight":Ssocial
    
      
        
    }
