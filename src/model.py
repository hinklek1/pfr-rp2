import cantera as ct
import numpy as np
from pint import UnitRegistry
ureg = UnitRegistry()
def to_si(q):
    return q.to_base_units().magnitude

def simulate(inputs, mechanism_path, kinetic_params=None, print_kinetics=False):
    # define mech and phases
    gas = ct.Solution(mechanism_path, name='gas')
    bulk = ct.Solution(mechanism_path, name='Cbulk')
    surf = ct.Interface(mechanism_path, name='surf', adjacent=[gas, bulk])
    
    # this was used to modify the kinetic parameters of the surface reactions for the optimization
    if kinetic_params is not None:
        # extract kinetic params from input
        As, Eas = np.asarray(kinetic_params[:surf.n_reactions]), np.asarray(kinetic_params[surf.n_reactions:])
        As = np.power(10, As+3) # unit conversions (should fix this)
        Eas = Eas*4.184*1e6     # unit conversions (should fix this)
        # modify kinetics of surface reactions
        for i, A, Ea in zip(range(surf.n_reactions),As,Eas):
            original_reaction = surf.reactions()[i]
            new_rate = ct.InterfaceArrheniusRate(A=A, b=0, Ea=Ea)  # need to check units on input data
            modified_reaction = ct.Reaction(
                reactants=original_reaction.reactants,
                products=original_reaction.products,
                rate=new_rate)
            surf.modify_reaction(i, modified_reaction)
    if print_kinetics:
        for i in range(surf.n_reactions):
            print(surf.reactions()[i].input_data)

    # set system parameters
    length = ureg.Quantity(inputs['length'][0]['value'], inputs['length'][1]['units'])
    diameter = ureg.Quantity(inputs['diameter'][0]['value'], inputs['diameter'][1]['units'])
    power = ureg.Quantity(inputs['power'][0]['value'], inputs['power'][1]['units'])
    volumetric_flow_rate = ureg.Quantity(inputs['volumetric_flow_rate'][0]['value'], inputs['volumetric_flow_rate'][1]['units'])
    N = inputs['number_of_slices'][0]['value']

    # convert to SI
    d = to_si(diameter)
    l = to_si(length)
    heat_added = to_si(power)

    # calculate additional parameters
    flow_area = 0.25 * np.pi * d * d
    wall_area = np.pi * d * l
    heat_per_length = heat_added / l
    dz = l / N

    # set reference temp
    T_ref = ureg.Quantity(300, 'K')

    # set Initial conditions
    T0 = ureg.Quantity(inputs['T0'][0]['value'], inputs['T0'][1]['units'])
    P0 = ureg.Quantity(inputs['P0'][0]['value'], inputs['P0'][1]['units'])
    X0 = 'RP2:1.0' # pure decane
    gas.TPX = to_si(T_ref), to_si(P0), X0
    density_ref = gas.density_mass
    gas.TPX = to_si(T0), to_si(P0), X0
    mass_flow_rate = density_ref * to_si(volumetric_flow_rate)
    mdot = mass_flow_rate
    H_in = gas.enthalpy_mass * mass_flow_rate
    surf.TP = to_si(T0), to_si(P0)
    surf.coverages = 'CC(s):1.0'

    # define reactor
    reactor = ct.Reactor(gas, clone=False)
    reactor.volume = flow_area * dz
    rsurf = ct.ReactorSurface(surf, reactor, A=dz*np.pi*d, clone=False)

    # set energy transfer
    heat_reservoir = ct.Reservoir(gas, clone=False)
    wall = ct.Wall(heat_reservoir, reactor, Q=heat_per_length * dz, A=1.0)

    upstream = ct.Reservoir(gas, name='upstream', clone=False)
    m = ct.MassFlowController(upstream, reactor, mdot=mass_flow_rate)

    downstream = ct.Reservoir(gas, name='downstream', clone=False)
    v = ct.PressureController(reactor, downstream, primary=m, K=1e-5)

    sim = ct.ReactorNet([reactor])
    sim.rtol = 1e-12  # relative tolerance
    sim.atol = 1e-24  # absolute tolerance
    soln = ct.SolutionArray(gas, extra=['z', 'surf_coverages', 'surf_rates', 'carbon_deposition_rate'])

    for ri in range(N):
        wdot = rsurf.phase.net_production_rates
        kC = surf.kinetics_species_index('C(B)')
        soln.append(TDY=reactor.phase.TDY, z=ri*dz, surf_coverages=rsurf.coverages, surf_rates=surf.net_rates_of_progress, carbon_deposition_rate=wdot[kC])
        # Set the state of the reservoir to match that of the previous reactor
        upstream.syncState()
            
        # integrate the reactor forward in time until steady state is reached
        sim.reinitialize()
        sim.advance_to_steady_state()  # runs until energy balance is achieved.
        
        #sim.advance(100000)  # this advances to a time, but results in less heat added (q_dot * dt)
    H_out = gas.enthalpy_mass * mass_flow_rate
    #mass_bulk = simpson(soln.Cdep,soln.z)
    Ebal = (H_in + heat_added) / (H_out) # + bulk.enthalpy_mass * mass_bulk)
    
    return soln