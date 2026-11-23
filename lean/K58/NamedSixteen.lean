import K58.NamedAutomorphisms

namespace K58

/-- Each image occupies one hexadecimal digit, with local position zero first. -/
private def wordMap (w : ℕ) (i : Fin 16) : Fin 16 := Fin.ofNat 16 (w >>> (4*i.val))

private def firstBranch (t : Bool) (v : Fin 16) :=
  PositionSearch.maps (template 16 t) (List.finRange 16).tail [0] (Function.update id 0 v)

private theorem splitFirst (t : Bool) : PositionSearch.automorphisms (template 16 t) =
    (List.finRange 16).flatMap (firstBranch t) := by rfl

set_option maxRecDepth 200000
set_option maxHeartbeats 0

private def bT0 : List (Fin 16 → Fin 16) := [0xfedcba9876543210, 0xc47f2a91d56e3b80].map wordMap
private theorem bT0_ok : bT0 = firstBranch true 0 := by decide +kernel

private def bT1 : List (Fin 16 → Fin 16) := [0xdcfeab8954762301, 0xe65d3b80f74c2a91].map wordMap
private theorem bT1_ok : bT1 = firstBranch true 1 := by decide +kernel

private def bT2 : List (Fin 16 → Fin 16) := [0xefcd98ba67451032, 0xd56e08b3c47f19a2].map wordMap
private theorem bT2_ok : bT2 = firstBranch true 2 := by decide +kernel

private def bT3 : List (Fin 16 → Fin 16) := [0xcdef89ab45670123, 0xf74c19a2e65d08b3].map wordMap
private theorem bT3_ok : bT3 = firstBranch true 3 := by decide +kernel

private def bT4 : List (Fin 16 → Fin 16) := [0xba98fedc32107654, 0x803b6ed5912a7fc4].map wordMap
private theorem bT4_ok : bT4 = firstBranch true 4 := by decide +kernel

private def bT5 : List (Fin 16 → Fin 16) := [0x98baefcd10326745, 0xa2197fc4b3086ed5].map wordMap
private theorem bT5_ok : bT5 = firstBranch true 5 := by decide +kernel

private def bT6 : List (Fin 16 → Fin 16) := [0xab89dcfe23015476, 0x912a4cf7803b5de6].map wordMap
private theorem bT6_ok : bT6 = firstBranch true 6 := by decide +kernel

private def bT7 : List (Fin 16 → Fin 16) := [0x89abcdef01234567, 0xb3085de6a2194cf7].map wordMap
private theorem bT7_ok : bT7 = firstBranch true 7 := by decide +kernel

private def bT8 : List (Fin 16 → Fin 16) := [0x7fc4a2196ed5b308, 0x45673210cdefba98].map wordMap
private theorem bT8_ok : bT8 = firstBranch true 8 := by decide +kernel

private def bT9 : List (Fin 16 → Fin 16) := [0x5de6b3084cf7a219, 0x67452301efcdab89].map wordMap
private theorem bT9_ok : bT9 = firstBranch true 9 := by decide +kernel

private def bT10 : List (Fin 16 → Fin 16) := [0x6ed5803b7fc4912a, 0x54761032dcfe98ba].map wordMap
private theorem bT10_ok : bT10 = firstBranch true 10 := by decide +kernel

private def bT11 : List (Fin 16 → Fin 16) := [0x4cf7912a5de6803b, 0x76540123fedc89ab].map wordMap
private theorem bT11_ok : bT11 = firstBranch true 11 := by decide +kernel

private def bT12 : List (Fin 16 → Fin 16) := [0x3b80e65d2a91f74c, 0x123765489abfedc].map wordMap
private theorem bT12_ok : bT12 = firstBranch true 12 := by decide +kernel

private def bT13 : List (Fin 16 → Fin 16) := [0x19a2f74c08b3e65d, 0x23016745ab89efcd].map wordMap
private theorem bT13_ok : bT13 = firstBranch true 13 := by decide +kernel

private def bT14 : List (Fin 16 → Fin 16) := [0x2a91c47f3b80d56e, 0x1032547698badcfe].map wordMap
private theorem bT14_ok : bT14 = firstBranch true 14 := by decide +kernel

private def bT15 : List (Fin 16 → Fin 16) := [0x8b3d56e19a2c47f, 0x32104567ba98cdef].map wordMap
private theorem bT15_ok : bT15 = firstBranch true 15 := by decide +kernel

private def blocksT : Fin 16 → List (Fin 16 → Fin 16) := ![bT0, bT1, bT2, bT3, bT4, bT5, bT6, bT7, bT8, bT9, bT10, bT11, bT12, bT13, bT14, bT15]
private theorem blocksT_ok (v : Fin 16) : blocksT v = firstBranch true v := by
  fin_cases v
  · exact bT0_ok
  · exact bT1_ok
  · exact bT2_ok
  · exact bT3_ok
  · exact bT4_ok
  · exact bT5_ok
  · exact bT6_ok
  · exact bT7_ok
  · exact bT8_ok
  · exact bT9_ok
  · exact bT10_ok
  · exact bT11_ok
  · exact bT12_ok
  · exact bT13_ok
  · exact bT14_ok
  · exact bT15_ok
private def bU0 : List (Fin 16 → Fin 16) := [0xfedcba9876543210, 0x89badcef76452310, 0x192a7f4cd5e6b380, 0xc47f2a91d56e3b80, 0xc6b1285f394ed7a0, 0xf528b16c39e47da0, 0xa6d13f482e59b7c0, 0x843fd16a2e957bc0, 0x1e3c785ab496d2f0, 0xa5783ce1b4692df0].map wordMap
private theorem bU0_ok : bU0 = firstBranch false 0 := by decide +kernel

private def bU1 : List (Fin 16 → Fin 16) := [0x98abcdfe67543201, 0xefcdab8967452301, 0x83b6e5dc4f7a291, 0xd56e3b80c47f2a91, 0xd7a0394e285fc6b1, 0xe439a07d28f56cb1, 0xb7c02e593f48a6d1, 0x952ec07b3f846ad1, 0xf2d694ba587c3e1, 0xb4692df0a5783ce1].map wordMap
private theorem bU1_ok : bU1 = firstBranch false 1 := by decide +kernel

private def bU2 : List (Fin 16 → Fin 16) := [0xdcfe98ba54761032, 0xab98fecd54670132, 0xe4930a7d1b6cf582, 0xd70a934e1bc65f82, 0x3b085d6ef7c491a2, 0xe65d08b3f74c19a2, 0x3c1e5a7896b4f0d2, 0x875a1ec3964b0fd2, 0x84f31d6a0c7b95e2, 0xa61df3480cb759e2].map wordMap
private theorem bU2_ok : bU2 = firstBranch false 2 := by decide +kernel

private def bU3 : List (Fin 16 → Fin 16) := [0xba89efdc45761023, 0xcdef89ab45670123, 0xf5821b6c0a7de493, 0xc61b825f0ad74e93, 0x2a194c7fe6d580b3, 0xf74c19a2e65d08b3, 0x2d0f4b6987a5e1c3, 0x964b0fd2875a1ec3, 0x95e20c7b1d6a84f3, 0xb70ce2591da648f3].map wordMap
private theorem bU3_ok : bU3 = firstBranch false 3 := by decide +kernel

private def bU4 : List (Fin 16 → Fin 16) := [0xba98fedc32107654, 0xcdfe98ab32016754, 0xe2957b0c6a1df384, 0xc07b952e6ad13f84, 0x5a783c1ef0d296b4, 0xe13c78a5f02d69b4, 0x5d6e3b0891a2f7c4, 0x803b6ed5912a7fc4, 0x82f56c1b7d0a93e4, 0xb16cf5287da039e4].map wordMap
private theorem bU4_ok : bU4 = firstBranch false 4 := by decide +kernel

private def bU5 : List (Fin 16 → Fin 16) := [0xdcef89ba23107645, 0xab89efcd23016745, 0xf3846a1d7b0ce295, 0xd16a843f7bc02e95, 0x4b692d0fe1c387a5, 0xf02d69b4e13c78a5, 0x4c7f2a1980b3e6d5, 0x912a7fc4803b6ed5, 0x93e47d0a6c1b82f5, 0xa07de4396cb128f5].map wordMap
private theorem bU5_ok : bU5 = firstBranch false 5 := by decide +kernel

private def bU6 : List (Fin 16 → Fin 16) := [0x98badcfe10325476, 0xefdcba8910234576, 0x785a1e3cd2f0b496, 0xc31e5a87d20f4b96, 0xc0b7592e483fd1a6, 0xe259b70c48f31da6, 0xa0d74e395f28b1c6, 0x934ed70a5f821bc6, 0x7f4c192ab380d5e6, 0xa2194cf7b3085de6].map wordMap
private theorem bU6_ok : bU6 = firstBranch false 6 := by decide +kernel

private def bU7 : List (Fin 16 → Fin 16) := [0xfecdab9801325467, 0x89abcdef01234567, 0x694b0f2dc3e1a587, 0xd20f4b96c31e5a87, 0xd1a6483f592ec0b7, 0xf348a61d59e20cb7, 0xb1c65f284e39a0d7, 0x825fc61b4e930ad7, 0x6e5d083ba291c4f7, 0xb3085de6a2194cf7].map wordMap
private theorem bU7_ok : bU7 = firstBranch false 7 := by decide +kernel

private def bU8 : List (Fin 16 → Fin 16) := [0x4cf7a2195de6b308, 0x91a2f7c45d6e3b08, 0x7da039e4b16cf528, 0x4e39a0d7b1c65f28, 0xcb759e2a61df348, 0x2e59b7c0a6d13f48, 0x2df0b4693ce1a578, 0x96b4f0d23c1e5a78, 0x76543210fedcba98, 0x1325467fecdab98].map wordMap
private theorem bU8_ok : bU8 = firstBranch false 8 := by decide +kernel

private def bU9 : List (Fin 16 → Fin 16) := [0x5de6b3084cf7a219, 0x80b3e6d54c7f2a19, 0x6cb128f5a07de439, 0x5f28b1c6a0d74e39, 0x1da648f3b70ce259, 0x3f48a6d1b7c02e59, 0x3ce1a5782df0b469, 0x87a5e1c32d0f4b69, 0x10234576efdcba89, 0x67452301efcdab89].map wordMap
private theorem bU9_ok : bU9 = firstBranch false 9 := by decide +kernel

private def bU10 : List (Fin 16 → Fin 16) := [0x5f821bc6934ed70a, 0x6c1b82f593e47d0a, 0x6ed5803b7fc4912a, 0xb380d5e67f4c192a, 0xfd2964b1ec3875a, 0xb496d2f01e3c785a, 0x2e957bc0843fd16a, 0xc7b95e284f31d6a, 0x54761032dcfe98ba, 0x23107645dcef89ba].map wordMap
private theorem bU10_ok : bU10 = firstBranch false 10 := by decide +kernel

private def bU11 : List (Fin 16 → Fin 16) := [0x4e930ad7825fc61b, 0x7d0a93e482f56c1b, 0x7fc4912a6ed5803b, 0xa291c4f76e5d083b, 0x1ec3875a0fd2964b, 0xa587c3e10f2d694b, 0x3f846ad1952ec07b, 0x1d6a84f395e20c7b, 0x32016754cdfe98ab, 0x45670123cdef89ab].map wordMap
private theorem bU11_ok : bU11 = firstBranch false 11 := by decide +kernel

private def bU12 : List (Fin 16 → Fin 16) := [0x48f31da6e259b70c, 0x6a1df384e2957b0c, 0x69b4f02d78a5e13c, 0xd2f0b496785a1e3c, 0x8b3e65d19a2f74c, 0xd5e6b380192a7f4c, 0x39e47da0f528b16c, 0xa7de493f5821b6c, 0x32107654ba98fedc, 0x45761023ba89efdc].map wordMap
private theorem bU12_ok : bU12 = firstBranch false 12 := by decide +kernel

private def bU13 : List (Fin 16 → Fin 16) := [0x59e20cb7f348a61d, 0x7b0ce295f3846a1d, 0x78a5e13c69b4f02d, 0xc3e1a587694b0f2d, 0x19a2f74c08b3e65d, 0xc4f7a291083b6e5d, 0x28f56cb1e439a07d, 0x1b6cf582e4930a7d, 0x54670132ab98fecd, 0x23016745ab89efcd].map wordMap
private theorem bU13_ok : bU13 = firstBranch false 13 := by decide +kernel

private def bU14 : List (Fin 16 → Fin 16) := [0x4b96d20f5a87c31e, 0xf0d296b45a783c1e, 0x6ad13f84c07b952e, 0x483fd1a6c0b7592e, 0x1bc65f82d70a934e, 0x285fc6b1d7a0394e, 0x2a91c47f3b80d56e, 0xf7c491a23b085d6e, 0x1032547698badcfe, 0x6754320198abcdfe].map wordMap
private theorem bU14_ok : bU14 = firstBranch false 14 := by decide +kernel

private def bU15 : List (Fin 16 → Fin 16) := [0x5a87c31e4b96d20f, 0xe1c387a54b692d0f, 0x7bc02e95d16a843f, 0x592ec0b7d1a6483f, 0xad74e93c61b825f, 0x394ed7a0c6b1285f, 0x3b80d56e2a91c47f, 0xe6d580b32a194c7f, 0x7645231089badcef, 0x123456789abcdef].map wordMap
private theorem bU15_ok : bU15 = firstBranch false 15 := by decide +kernel

private def blocksU : Fin 16 → List (Fin 16 → Fin 16) := ![bU0, bU1, bU2, bU3, bU4, bU5, bU6, bU7, bU8, bU9, bU10, bU11, bU12, bU13, bU14, bU15]
private theorem blocksU_ok (v : Fin 16) : blocksU v = firstBranch false v := by
  fin_cases v
  · exact bU0_ok
  · exact bU1_ok
  · exact bU2_ok
  · exact bU3_ok
  · exact bU4_ok
  · exact bU5_ok
  · exact bU6_ok
  · exact bU7_ok
  · exact bU8_ok
  · exact bU9_ok
  · exact bU10_ok
  · exact bU11_ok
  · exact bU12_ok
  · exact bU13_ok
  · exact bU14_ok
  · exact bU15_ok

/-- Complete ordered named-colour automorphism table, assembled by first image. -/
def named16 (t : Bool) : List (Fin 16 → Fin 16) :=
  (List.finRange 16).flatMap (if t then blocksT else blocksU)

theorem named16_exact (t : Bool) : named16 t = PositionSearch.automorphisms (template 16 t) := by
  rw [splitFirst]
  cases t
  · exact congrArg (List.flatMap · (List.finRange 16)) (funext blocksU_ok)
  · exact congrArg (List.flatMap · (List.finRange 16)) (funext blocksT_ok)

end K58
