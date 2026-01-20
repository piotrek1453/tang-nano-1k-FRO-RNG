generate_block_diagrams:
	yosys -p "read_verilog ring_oscillator.v top.v; hierarchy -top top; show -format svg -prefix fro_rng top"
	yosys -p "read_verilog ring_oscillator.v top.v; hierarchy -top top; proc; opt; show -format svg -prefix fro_rng_rtl top"
