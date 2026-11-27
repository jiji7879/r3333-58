# Audit the 24-pattern continuation of signed case 0

The attachment `K58_case0_24_patterns.zip` claims that all seven initially
unresolved pivot-0 words and seventeen pivot-3 words have now been refuted.
It concludes that on the supplied full signed parent, the two trigger
assumptions $(31,13)=0$ and $(42,13)=1$ cannot both hold, giving the binary
clause `-2721 -2766 0`.

Check whether the finite cover and actual proof bytes imply this conclusion
for precisely this signed representative, with physical literal numbering and
all predecessor case boundaries intact. Check the claimed 7+17 patterns,
69+148 arm alternatives, absence of residual leaves, and statement that no
unconditional pivot branch or Ramsey bound is thereby closed. `OPEN` is not
SAT; a local model is not a full K58 model. Do not mutate production state or
transfer the conditional clause to other representatives without a proof.
