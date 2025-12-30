`default_nettype none

module top #(
    parameter integer CLOCK_DIVIDER = 27  //! on Tang Nano 1k - drop output data rate to 1 Mbit/s
) (
    input  wire clkIn,
    output wire generatorOut,
    output wire clkOut
);
  // clock for synchronizing the output bitstream
  reg divided_clk = 'b0;

  // ROs outputs
  wire [4:0] ring_oscillator_out;

  // counter for dividing clock
  reg [$clog2(CLOCK_DIVIDER)-1:0] clk_div_counter = 'd0;

  // raw entropy output and entropy synced to output clock
  reg entropy_bit, synced_entropy;

  // ring oscillators: entropy sources from jitter
  ring_oscillator #(
      .INVERTERS_COUNT(5)
  ) osc0 (
      .enable(1'b1),
      .oscillatorOut(ring_oscillator_out[0])
  );
  ring_oscillator #(
      .INVERTERS_COUNT(7)
  ) osc1 (
      .enable(1'b1),
      .oscillatorOut(ring_oscillator_out[1])
  );
  ring_oscillator #(
      .INVERTERS_COUNT(9)
  ) osc2 (
      .enable(1'b1),
      .oscillatorOut(ring_oscillator_out[2])
  );
  ring_oscillator #(
      .INVERTERS_COUNT(11)
  ) osc3 (
      .enable(1'b1),
      .oscillatorOut(ring_oscillator_out[3])
  );
  ring_oscillator #(
      .INVERTERS_COUNT(13)
  ) osc4 (
      .enable(1'b1),
      .oscillatorOut(ring_oscillator_out[4])
  );

  // divide the input clock, sample entropy bit
  always @(posedge clkIn) begin
    // input clock division
    if (clk_div_counter == integer(CLOCK_DIVIDER / 2 - 1)) begin
      clk_div_counter <= 'd0;
      divided_clk <= ~divided_clk;

      // XORed RO outputs are raw entropy output
      entropy_bit <= ^ring_oscillator_out;
    end else begin
      clk_div_counter <= clk_div_counter + 1;
    end
  end

  // output the random bit at rising edge of divided clock
  always @(posedge divided_clk) begin
    synced_entropy <= entropy_bit;
  end


  // final generator output with additional whitening
  assign generatorOut = synced_entropy;
  // sync output
  assign clkOut = divided_clk;


endmodule
