import SemanticAssembly

open K58
open K58.SequentialCounter
open K58.EncoderExtensions
open K58.SemanticAssembly

/-- Lookup an input vector, defaulting to the impossible variable zero. -/
def listAtoms (xs : List Nat) : Nat → Nat := fun i => xs.getD i 0

/-- Membership bit for one catalogue support. -/
def supportBit (supports : List (List Nat)) {k : Nat} (i : Fin k) (j : Nat) : Bool :=
  (supports.getD i.val []).contains j

def targetSupports : List (List Nat) :=
  [[0,2,4,6], [0,2,4,7], [0,2,4,9], [0,2,5,6], [0,2,5,7], [0,2,5,11], [0,2,6,11], [0,2,7,9], [0,3,4,6], [0,3,4,13], [0,3,5,7], [0,3,5,14], [0,3,6,13], [0,3,7,14], [0,4,6,13], [0,4,7,9], [0,5,6,11], [0,5,7,14], [0,5,11,14], [0,6,11,13], [0,9,11,13], [0,9,11,14], [0,9,13,14], [0,11,13,14], [1,2,4,6], [1,2,4,15], [1,2,5,7], [1,2,5,12], [1,2,6,15], [1,2,7,12], [1,3,4,6], [1,3,4,7], [1,3,4,10], [1,3,5,6], [1,3,5,7], [1,3,5,8], [1,3,6,8], [1,3,7,10], [1,4,6,15], [1,4,7,10], [1,4,10,15], [1,5,6,8], [1,5,7,12], [1,7,10,12], [1,8,10,12], [1,8,10,15], [1,8,12,15], [1,10,12,15], [2,4,6,15], [2,4,7,9], [2,4,9,15], [2,5,6,11], [2,5,7,12], [2,7,9,12], [2,9,11,12], [2,9,11,15], [2,9,12,15], [2,11,12,15], [3,4,6,13], [3,4,7,10], [3,5,6,8], [3,5,7,14], [3,5,8,14], [3,6,8,13], [3,8,10,13], [3,8,10,14], [3,8,13,14], [3,10,13,14], [4,9,10,13], [4,9,10,15], [4,9,13,15], [4,10,13,15], [5,8,11,12], [5,8,11,14], [5,8,12,14], [5,11,12,14], [6,8,11,13], [6,8,11,15], [6,8,13,15], [6,11,13,15], [7,9,10,12], [7,9,10,14], [7,9,12,14], [7,10,12,14], [8,10,12,14], [8,10,12,15], [8,10,13,14], [8,10,13,15], [8,11,12,14], [8,11,13,15], [9,10,12,14], [9,10,13,15], [9,11,12,14], [9,11,12,15], [9,11,13,14], [9,11,13,15], [0,2,4,7,9], [0,2,5,6,11], [0,3,4,6,13], [0,3,5,7,14], [0,9,11,13,14], [1,2,4,6,15], [1,2,5,7,12], [1,3,4,7,10], [1,3,5,6,8], [1,8,10,12,15], [2,9,11,12,15], [3,8,10,13,14], [4,9,10,13,15], [5,8,11,12,14], [6,8,11,13,15], [7,9,10,12,14]]

/-- Exact linked allocation of all extra clauses in parent 90d06e.... -/
def targetSuffixSteps : List ExtensionStep := [
  freshGuardedCounterStepAuto
    6612 6613 30 10 6813 (listAtoms [293,297,301,305,309,313,317,321,325,329,333,337,341,345,349,373,377,381,385,389,393,397,401,405,429,433,437,441,445,449])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    6813 6814 41 14 7192 (listAtoms [509,513,517,521,525,529,533,537,541,545,549,553,557,561,565,569,573,577,581,585,589,593,597,601,605,609,613,617,621,625,629,633,637,641,645,649,653,657,661,665,669])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    7192 7193 30 10 7393 (listAtoms [729,733,737,741,745,749,753,757,761,765,769,773,777,781,785,809,813,817,821,825,829,833,837,841,865,869,873,877,881,885])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    7393 7394 41 14 7772 (listAtoms [937,941,945,949,953,957,961,965,969,973,977,981,985,989,993,997,1001,1005,1009,1013,1017,1021,1025,1029,1033,1037,1041,1045,1049,1053,1057,1061,1065,1069,1073,1077,1081,1085,1089,1093,1097])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    7772 7773 41 14 8151 (listAtoms [1145,1149,1153,1157,1161,1165,1169,1173,1177,1181,1185,1189,1193,1197,1201,1205,1209,1213,1217,1221,1225,1229,1233,1237,1241,1245,1249,1253,1257,1261,1265,1269,1273,1277,1281,1285,1289,1293,1297,1301,1305])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    8151 8152 41 14 8530 (listAtoms [1349,1353,1357,1361,1365,1369,1373,1377,1381,1385,1389,1393,1397,1401,1405,1409,1413,1417,1421,1425,1429,1433,1437,1441,1445,1449,1453,1457,1461,1465,1469,1473,1477,1481,1485,1489,1493,1497,1501,1505,1509])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    8530 8531 30 10 8731 (listAtoms [1553,1557,1561,1565,1569,1573,1577,1581,1585,1589,1593,1597,1601,1605,1609,1633,1637,1641,1645,1649,1653,1657,1661,1665,1689,1693,1697,1701,1705,1709])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    8731 8732 41 14 9110 (listAtoms [1745,1749,1753,1757,1761,1765,1769,1773,1777,1781,1785,1789,1793,1797,1801,1805,1809,1813,1817,1821,1825,1829,1833,1837,1841,1845,1849,1853,1857,1861,1865,1869,1873,1877,1881,1885,1889,1893,1897,1901,1905])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    9110 9111 41 14 9489 (listAtoms [1937,1941,1945,1949,1953,1957,1961,1965,1969,1973,1977,1981,1985,1989,1993,1997,2001,2005,2009,2013,2017,2021,2025,2029,2033,2037,2041,2045,2049,2053,2057,2061,2065,2069,2073,2077,2081,2085,2089,2093,2097])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    9489 9490 41 14 9868 (listAtoms [2125,2129,2133,2137,2141,2145,2149,2153,2157,2161,2165,2169,2173,2177,2181,2185,2189,2193,2197,2201,2205,2209,2213,2217,2221,2225,2229,2233,2237,2241,2245,2249,2253,2257,2261,2265,2269,2273,2277,2281,2285])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    9868 9869 41 14 10247 (listAtoms [2309,2313,2317,2321,2325,2329,2333,2337,2341,2345,2349,2353,2357,2361,2365,2369,2373,2377,2381,2385,2389,2393,2397,2401,2405,2409,2413,2417,2421,2425,2429,2433,2437,2441,2445,2449,2453,2457,2461,2465,2469])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    10247 10248 30 10 10448 (listAtoms [2493,2497,2501,2505,2509,2513,2517,2521,2525,2529,2533,2537,2541,2545,2549,2573,2577,2581,2585,2589,2593,2597,2601,2605,2629,2633,2637,2641,2645,2649])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    10448 10449 41 14 10827 (listAtoms [2665,2669,2673,2677,2681,2685,2689,2693,2697,2701,2705,2709,2713,2717,2721,2725,2729,2733,2737,2741,2745,2749,2753,2757,2761,2765,2769,2773,2777,2781,2785,2789,2793,2797,2801,2805,2809,2813,2817,2821,2825])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    10827 10828 41 14 11206 (listAtoms [2837,2841,2845,2849,2853,2857,2861,2865,2869,2873,2877,2881,2885,2889,2893,2897,2901,2905,2909,2913,2917,2921,2925,2929,2933,2937,2941,2945,2949,2953,2957,2961,2965,2969,2973,2977,2981,2985,2989,2993,2997])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    11206 11207 41 14 11585 (listAtoms [3005,3009,3013,3017,3021,3025,3029,3033,3037,3041,3045,3049,3053,3057,3061,3065,3069,3073,3077,3081,3085,3089,3093,3097,3101,3105,3109,3113,3117,3121,3125,3129,3133,3137,3141,3145,3149,3153,3157,3161,3165])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    11585 11586 41 14 11964 (listAtoms [3169,3173,3177,3181,3185,3189,3193,3197,3201,3205,3209,3213,3217,3221,3225,3229,3233,3237,3241,3245,3249,3253,3257,3261,3265,3269,3273,3277,3281,3285,3289,3293,3297,3301,3305,3309,3313,3317,3321,3325,3329])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  freshGuardedCounterStepAuto
    11964 11965 41 14 12343 (listAtoms [294,514,730,942,1150,1354,1554,1750,1942,2130,2314,2494,2670,2842,3010,3174,3550,3554,3558,3562,3566,3570,3574,3578,3582,3586,3590,3594,3598,3602,3606,3610,3614,3618,3622,3626,3630,3634,3638,3642,3646])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    12343 11965 16 112 12455 (listAtoms [294,514,730,942,1150,1354,1554,1750,1942,2130,2314,2494,2670,2842,3010,3174])
    (fun i => 12344 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 12344 + i.val = 12344 + j.val at h; omega)
    (emittedSupport_varsBelow 11965 16 112 12343 12455 (listAtoms [294,514,730,942,1150,1354,1554,1750,1942,2130,2314,2494,2670,2842,3010,3174])
      (fun i => 12344 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    12455 12456 41 14 12834 (listAtoms [298,518,734,946,1154,1358,1558,1754,1946,2134,2318,2498,2674,2846,3014,3178,3702,3706,3710,3714,3718,3722,3726,3730,3734,3738,3742,3746,3750,3754,3758,3762,3766,3770,3774,3778,3782,3786,3790,3794,3798])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    12834 12456 16 112 12946 (listAtoms [298,518,734,946,1154,1358,1558,1754,1946,2134,2318,2498,2674,2846,3014,3178])
    (fun i => 12835 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 12835 + i.val = 12835 + j.val at h; omega)
    (emittedSupport_varsBelow 12456 16 112 12834 12946 (listAtoms [298,518,734,946,1154,1358,1558,1754,1946,2134,2318,2498,2674,2846,3014,3178])
      (fun i => 12835 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    12946 12947 41 14 13325 (listAtoms [302,522,738,950,1158,1362,1562,1758,1950,2138,2322,2502,2678,2850,3018,3182,3850,3854,3858,3862,3866,3870,3874,3878,3882,3886,3890,3894,3898,3902,3906,3910,3914,3918,3922,3926,3930,3934,3938,3942,3946])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    13325 12947 16 112 13437 (listAtoms [302,522,738,950,1158,1362,1562,1758,1950,2138,2322,2502,2678,2850,3018,3182])
    (fun i => 13326 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 13326 + i.val = 13326 + j.val at h; omega)
    (emittedSupport_varsBelow 12947 16 112 13325 13437 (listAtoms [302,522,738,950,1158,1362,1562,1758,1950,2138,2322,2502,2678,2850,3018,3182])
      (fun i => 13326 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    13437 13438 41 14 13816 (listAtoms [306,526,742,954,1162,1366,1566,1762,1954,2142,2326,2506,2682,2854,3022,3186,3994,3998,4002,4006,4010,4014,4018,4022,4026,4030,4034,4038,4042,4046,4050,4054,4058,4062,4066,4070,4074,4078,4082,4086,4090])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    13816 13438 16 112 13928 (listAtoms [306,526,742,954,1162,1366,1566,1762,1954,2142,2326,2506,2682,2854,3022,3186])
    (fun i => 13817 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 13817 + i.val = 13817 + j.val at h; omega)
    (emittedSupport_varsBelow 13438 16 112 13816 13928 (listAtoms [306,526,742,954,1162,1366,1566,1762,1954,2142,2326,2506,2682,2854,3022,3186])
      (fun i => 13817 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    13928 13929 41 14 14307 (listAtoms [310,530,746,958,1166,1370,1570,1766,1958,2146,2330,2510,2686,2858,3026,3190,4134,4138,4142,4146,4150,4154,4158,4162,4166,4170,4174,4178,4182,4186,4190,4194,4198,4202,4206,4210,4214,4218,4222,4226,4230])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    14307 13929 16 112 14419 (listAtoms [310,530,746,958,1166,1370,1570,1766,1958,2146,2330,2510,2686,2858,3026,3190])
    (fun i => 14308 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 14308 + i.val = 14308 + j.val at h; omega)
    (emittedSupport_varsBelow 13929 16 112 14307 14419 (listAtoms [310,530,746,958,1166,1370,1570,1766,1958,2146,2330,2510,2686,2858,3026,3190])
      (fun i => 14308 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    14419 14420 41 14 14798 (listAtoms [314,534,750,962,1170,1374,1574,1770,1962,2150,2334,2514,2690,2862,3030,3194,4270,4274,4278,4282,4286,4290,4294,4298,4302,4306,4310,4314,4318,4322,4326,4330,4334,4338,4342,4346,4350,4354,4358,4362,4366])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    14798 14420 16 112 14910 (listAtoms [314,534,750,962,1170,1374,1574,1770,1962,2150,2334,2514,2690,2862,3030,3194])
    (fun i => 14799 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 14799 + i.val = 14799 + j.val at h; omega)
    (emittedSupport_varsBelow 14420 16 112 14798 14910 (listAtoms [314,534,750,962,1170,1374,1574,1770,1962,2150,2334,2514,2690,2862,3030,3194])
      (fun i => 14799 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    14910 14911 41 14 15289 (listAtoms [318,538,754,966,1174,1378,1578,1774,1966,2154,2338,2518,2694,2866,3034,3198,4402,4406,4410,4414,4418,4422,4426,4430,4434,4438,4442,4446,4450,4454,4458,4462,4466,4470,4474,4478,4482,4486,4490,4494,4498])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    15289 14911 16 112 15401 (listAtoms [318,538,754,966,1174,1378,1578,1774,1966,2154,2338,2518,2694,2866,3034,3198])
    (fun i => 15290 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 15290 + i.val = 15290 + j.val at h; omega)
    (emittedSupport_varsBelow 14911 16 112 15289 15401 (listAtoms [318,538,754,966,1174,1378,1578,1774,1966,2154,2338,2518,2694,2866,3034,3198])
      (fun i => 15290 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    15401 15402 41 14 15780 (listAtoms [322,542,758,970,1178,1382,1582,1778,1970,2158,2342,2522,2698,2870,3038,3202,4530,4534,4538,4542,4546,4550,4554,4558,4562,4566,4570,4574,4578,4582,4586,4590,4594,4598,4602,4606,4610,4614,4618,4622,4626])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    15780 15402 16 112 15892 (listAtoms [322,542,758,970,1178,1382,1582,1778,1970,2158,2342,2522,2698,2870,3038,3202])
    (fun i => 15781 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 15781 + i.val = 15781 + j.val at h; omega)
    (emittedSupport_varsBelow 15402 16 112 15780 15892 (listAtoms [322,542,758,970,1178,1382,1582,1778,1970,2158,2342,2522,2698,2870,3038,3202])
      (fun i => 15781 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    15892 15893 41 14 16271 (listAtoms [326,546,762,974,1182,1386,1586,1782,1974,2162,2346,2526,2702,2874,3042,3206,4654,4658,4662,4666,4670,4674,4678,4682,4686,4690,4694,4698,4702,4706,4710,4714,4718,4722,4726,4730,4734,4738,4742,4746,4750])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    16271 15893 16 112 16383 (listAtoms [326,546,762,974,1182,1386,1586,1782,1974,2162,2346,2526,2702,2874,3042,3206])
    (fun i => 16272 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 16272 + i.val = 16272 + j.val at h; omega)
    (emittedSupport_varsBelow 15893 16 112 16271 16383 (listAtoms [326,546,762,974,1182,1386,1586,1782,1974,2162,2346,2526,2702,2874,3042,3206])
      (fun i => 16272 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    16383 16384 41 14 16762 (listAtoms [330,550,766,978,1186,1390,1590,1786,1978,2166,2350,2530,2706,2878,3046,3210,4774,4778,4782,4786,4790,4794,4798,4802,4806,4810,4814,4818,4822,4826,4830,4834,4838,4842,4846,4850,4854,4858,4862,4866,4870])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    16762 16384 16 112 16874 (listAtoms [330,550,766,978,1186,1390,1590,1786,1978,2166,2350,2530,2706,2878,3046,3210])
    (fun i => 16763 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 16763 + i.val = 16763 + j.val at h; omega)
    (emittedSupport_varsBelow 16384 16 112 16762 16874 (listAtoms [330,550,766,978,1186,1390,1590,1786,1978,2166,2350,2530,2706,2878,3046,3210])
      (fun i => 16763 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    16874 16875 41 14 17253 (listAtoms [334,554,770,982,1190,1394,1594,1790,1982,2170,2354,2534,2710,2882,3050,3214,4890,4894,4898,4902,4906,4910,4914,4918,4922,4926,4930,4934,4938,4942,4946,4950,4954,4958,4962,4966,4970,4974,4978,4982,4986])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    17253 16875 16 112 17365 (listAtoms [334,554,770,982,1190,1394,1594,1790,1982,2170,2354,2534,2710,2882,3050,3214])
    (fun i => 17254 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 17254 + i.val = 17254 + j.val at h; omega)
    (emittedSupport_varsBelow 16875 16 112 17253 17365 (listAtoms [334,554,770,982,1190,1394,1594,1790,1982,2170,2354,2534,2710,2882,3050,3214])
      (fun i => 17254 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    17365 17366 41 14 17744 (listAtoms [338,558,774,986,1194,1398,1598,1794,1986,2174,2358,2538,2714,2886,3054,3218,5002,5006,5010,5014,5018,5022,5026,5030,5034,5038,5042,5046,5050,5054,5058,5062,5066,5070,5074,5078,5082,5086,5090,5094,5098])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    17744 17366 16 112 17856 (listAtoms [338,558,774,986,1194,1398,1598,1794,1986,2174,2358,2538,2714,2886,3054,3218])
    (fun i => 17745 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 17745 + i.val = 17745 + j.val at h; omega)
    (emittedSupport_varsBelow 17366 16 112 17744 17856 (listAtoms [338,558,774,986,1194,1398,1598,1794,1986,2174,2358,2538,2714,2886,3054,3218])
      (fun i => 17745 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    17856 17857 41 14 18235 (listAtoms [342,562,778,990,1198,1402,1602,1798,1990,2178,2362,2542,2718,2890,3058,3222,5110,5114,5118,5122,5126,5130,5134,5138,5142,5146,5150,5154,5158,5162,5166,5170,5174,5178,5182,5186,5190,5194,5198,5202,5206])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    18235 17857 16 112 18347 (listAtoms [342,562,778,990,1198,1402,1602,1798,1990,2178,2362,2542,2718,2890,3058,3222])
    (fun i => 18236 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 18236 + i.val = 18236 + j.val at h; omega)
    (emittedSupport_varsBelow 17857 16 112 18235 18347 (listAtoms [342,562,778,990,1198,1402,1602,1798,1990,2178,2362,2542,2718,2890,3058,3222])
      (fun i => 18236 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    18347 18348 41 14 18726 (listAtoms [346,566,782,994,1202,1406,1606,1802,1994,2182,2366,2546,2722,2894,3062,3226,5214,5218,5222,5226,5230,5234,5238,5242,5246,5250,5254,5258,5262,5266,5270,5274,5278,5282,5286,5290,5294,5298,5302,5306,5310])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    18726 18348 16 112 18838 (listAtoms [346,566,782,994,1202,1406,1606,1802,1994,2182,2366,2546,2722,2894,3062,3226])
    (fun i => 18727 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 18727 + i.val = 18727 + j.val at h; omega)
    (emittedSupport_varsBelow 18348 16 112 18726 18838 (listAtoms [346,566,782,994,1202,1406,1606,1802,1994,2182,2366,2546,2722,2894,3062,3226])
      (fun i => 18727 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  freshGuardedCounterStepAuto
    18838 18839 41 14 19217 (listAtoms [350,570,786,998,1206,1410,1610,1806,1998,2186,2370,2550,2726,2898,3066,3230,5314,5318,5322,5326,5330,5334,5338,5342,5346,5350,5354,5358,5362,5366,5370,5374,5378,5382,5386,5390,5394,5398,5402,5406,5410])
    (by omega) (by decide) (by intro i hi; interval_cases i <;> decide),
  emittedSupportStep
    19217 18839 16 112 19329 (listAtoms [350,570,786,998,1206,1410,1610,1806,1998,2186,2370,2550,2726,2898,3066,3230])
    (fun i => 19218 + i.val) (supportBit targetSupports) (fun _ => true)
    (by omega) (by omega) (by intro i hi; interval_cases i <;> decide)
    (by intro i; have hi := i.isLt; omega) (by intro i j h; apply Fin.ext; change 19218 + i.val = 19218 + j.val at h; omega)
    (emittedSupport_varsBelow 18839 16 112 19217 19329 (listAtoms [350,570,786,998,1206,1410,1610,1806,1998,2186,2370,2550,2726,2898,3066,3230])
      (fun i => 19218 + i.val) (supportBit targetSupports) (fun _ => true)
      (by omega) (by omega)
      (by intro i hi; interval_cases i <;> decide) (by intro i; have hi := i.isLt; omega)),
  nativeCounterStepAuto
    19329 15 6 19383 (listAtoms [11965,12456,12947,13438,13929,14420,14911,15402,15893,16384,16875,17366,17857,18348,18839])
    (by decide) (by intro i hi; interval_cases i <;> decide),
  nativeCounterStepAuto
    19383 31 6 19533 (listAtoms [6613,6814,7193,7394,7773,8152,8531,8732,9111,9490,9869,10248,10449,10828,11207,11586,11965,12456,12947,13438,13929,14420,14911,15402,15893,16384,16875,17366,17857,18348,18839])
    (by decide) (by intro i hi; interval_cases i <;> decide),
]

def targetSuffixCNF : CNF := targetSuffixSteps.flatMap ExtensionStep.clauses

/-- Conditional exact-row suffix assembly: the remaining content is precisely
`ChainReady`, namely support geometry and the two final guard-count premises
(plus definitional links which can be checked separately). -/
theorem targetSuffix_satisfiable_of_ready (v : Valuation)
    (h : ChainReady 6612 v targetSuffixSteps) :
    ∃ w : Valuation, (∀ a ≤ 6612, w a = v a) ∧ FormulaSat w targetSuffixCNF := by
  exact chain_extend targetSuffixSteps 6612 v h

#print axioms targetSuffix_satisfiable_of_ready

-- DIMACS stream uses a leading metadata line, stripped by the byte checker.
#eval do
  IO.println s!"COUNT {targetSuffixCNF.length}"
  for c in targetSuffixCNF do
    let fields := c.map (fun (l : Bool × Nat) => if l.1 then toString l.2 else "-" ++ toString l.2)
    IO.println ((String.intercalate " " fields) ++ " 0")
