import unittest
from vcd_state_ledger import analyze

H='$timescale 1 ns $end $scope module top $end $var wire 1 ! clk $end $var wire 2 " bus $end $var wire 1 ! alias $end $upscope $end $enddefinitions $end '
BODY='$dumpvars 0! b10 " $end #5 1! bxx " #10 0! b01 " #12'

class WaveTests(unittest.TestCase):
    def test_exact_bit_time_with_alias(self):
        r=analyze(H+BODY,15);s=r['signals'];self.assertEqual(s[0]['bit_ticks'],{'0':10,'1':5,'x':0,'z':0});self.assertEqual(s[1]['bit_ticks'],{'0':10,'1':10,'x':10,'z':0});self.assertEqual(s[0]['names'],['top.alias','top.clk']);self.assertEqual(r['unknown_bit_ticks'],10)
    def test_duration_conservation(self):
        for end in [12,15,1000]:
            for s in analyze(H+BODY,end)['signals']:self.assertEqual(sum(s['bit_ticks'].values()),s['width']*end)
    def test_same_tick_glitches_no_duration(self):
        r=analyze(H+'#0 0! #5 1! 0! 1! #10',10);s=r['signals'][0];self.assertEqual((s['rising_edges'],s['falling_edges']),(2,1));self.assertEqual(s['bit_ticks']['1'],5)
    def test_redundant_value_not_transition(self):
        r=analyze(H+'0! 0! #10');self.assertEqual(r['signals'][0]['value_changes'],1)
    def test_initial_unknown_is_accounted(self):
        r=analyze(H+'#5 0! #10');self.assertEqual(r['signals'][0]['bit_ticks']['x'],5)
    def test_short_binary_padding(self):
        r=analyze(H+'b1 " #10');self.assertEqual(r['signals'][1]['value'],'01')
    def test_short_xz_padding(self):
        for v in ['x','z']:
            r=analyze(H+'b'+v+' " #10');self.assertEqual(r['signals'][1]['bit_ticks'][v],20)
    def test_timescale(self):
        self.assertEqual(analyze(H.replace('1 ns','100 ps')+'#10')['timescale']['femtoseconds_per_tick'],100000)
    def test_whitespace_and_inline_timestamps(self):
        a=analyze(H+BODY);b=analyze((H+BODY).replace(' ','\n'));self.assertEqual(a,b)
    def test_comments_ignore_tokens(self):
        self.assertEqual(analyze(H+'$comment #900 imaginary $end '+BODY),analyze(H+BODY))
    def test_monotonicity(self):
        with self.assertRaises(ValueError):analyze(H+'#10 #9')
    def test_unknown_signal(self):
        with self.assertRaises(ValueError):analyze(H+'0absent #10')
    def test_bad_width(self):
        for text in [H.replace('wire 2','wire 0'),H.replace('wire 2','wire 257')]:
            with self.assertRaises(ValueError):analyze(text+BODY)
    def test_alias_width(self):
        with self.assertRaisesRegex(ValueError,'alias widths'):analyze(H.replace('wire 1 ! alias','wire 2 ! alias')+BODY)
    def test_duplicate_name(self):
        with self.assertRaises(ValueError):analyze(H.replace('alias','clk')+BODY)
    def test_malformed_value(self):
        for body in ['b101 " #10','b2 " #10','1" #10','b1','#-1']:
            with self.subTest(body=body),self.assertRaises(ValueError):analyze(H+body)
    def test_unsupported_dump_and_real(self):
        for b in ['$dumpoff $end #10','r1.2 ! #10']:
            with self.assertRaises(ValueError):analyze(H+b)
    def test_end_override_explicit(self):
        for end in [0,11,-1,True,10**15]:
            with self.assertRaises(ValueError):analyze(H+BODY,end)
    def test_incomplete_headers_or_dump(self):
        for t in ['$timescale 1ns',H.replace('$enddefinitions $end',''),H+'$dumpvars 0!']:
            with self.assertRaises(ValueError):analyze(t,10)
    def test_missing_timescale_unbalanced_scope(self):
        for h in [H.replace('$timescale 1 ns $end',''),H.replace('$upscope $end','')]:
            with self.assertRaises(ValueError):analyze(h+BODY)

if __name__=='__main__':unittest.main()
