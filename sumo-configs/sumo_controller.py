import traci
import time

# Path to your SUMO config file
sumo_cmd = ["sumo-gui", "-c", "grid_tl.sumocfg"]

# Start SUMO with TraCI
traci.start(sumo_cmd)
print("Connected to SUMO successfully!")

# Get list of traffic lights
tls_ids = traci.trafficlight.getIDList()
print("Traffic lights:", tls_ids)

# Run for 1000 simulation steps
for step in range(1000):
    traci.simulationStep()

    for tls in tls_ids:
        current_phase = traci.trafficlight.getPhase(tls)
        print(f"Step {step} - Light {tls} phase: {current_phase}")

        # Example: change signal every 50 steps
        if step % 50 == 0:
            next_phase = (current_phase + 1) % traci.trafficlight.getPhaseNumber(tls)
            traci.trafficlight.setPhase(tls, next_phase)
    
    time.sleep(0.1)

traci.close()
print("Simulation ended.")
