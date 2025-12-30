`default_nettype none

module ring_oscillator #(
    parameter integer INVERTERS_COUNT = 7 //! number of inverters in generator, only odd number makes sense
) (
    input wire enable,  //! if logical '1' oscillator enabled, disabled otherwise
    output wire oscillatorOut  //! output signal of the oscillator
);
  // Don't optimize the RO away in Gowin synthesis tools
  (* syn_keep = "true" *) wire [INVERTERS_COUNT:0] stages;

  // Feedback loop with enable control
  // When enable is low, breaks the feedback loop and stops oscillation
  assign stages[0] = enable & stages[INVERTERS_COUNT];

  // Generate inverters in series
  genvar i;
  generate
    for (i = 0; i < INVERTERS_COUNT; i = i + 1) begin : inverter_chain
      assign stages[i+1] = ~stages[i];
    end
  endgenerate

  // Connect output of last inverter to oscillatorOut
  assign oscillatorOut = stages[INVERTERS_COUNT];

endmodule
