import math

'''
Created by Marco Jakob

Source: http://depts.washington.edu/madlab/proj/dollar/index.html
'''

NumTemplates = 16
NumPoints = 64
SquareSize = 250.0
HalfDiagonal = 0.5 * math.sqrt(250.0 * 250.0 + 250.0 * 250.0)
AngleRange = 45.0
AnglePrecision = 2.0
Phi = 0.5 * (-1.0 + math.sqrt(5.0))  # Golden Ratio
minPoints = 60


class GestureTemplate:
    def __init__(self, name2, points2):
        self.Name = name2
        self.Points = points2

        self.Points = dollar_resample(self.Points, NumPoints)
        self.Points = rotate_to_zero(self.Points)
        self.Points = scale_to_square(self.Points, SquareSize)
        self.Points = TranslateToOrigin(self.Points)


class RecogResult:
    def __init__(self, name2, score2):
        self.Name = name2
        self.Score = score2


class DollarRecognizer:
    def __init__(self):
        # predefined templates
        self.templates = []
        self.templates.append(
            GestureTemplate('Swipe down', [(957, 249), (956, 251), (955.5343906859862, 252.1640232850345),
                                           (954.238326573435, 255.40418356641248), (954, 256),
                                           (953.4414523267023, 258.7927383664885),
                                           (952.7570541960328, 262.2147290198361),
                                           (952.0726560653633, 265.6367196731838), (952, 266),
                                           (951.558866523236, 269.0879343373481),
                                           (951.0653400126439, 272.54261991149303), (951, 273),
                                           (950.2033500205845, 275.9210499245234),
                                           (949.285133574274, 279.28784356099527),
                                           (948.3669171279635, 282.65463719746714), (948, 284),
                                           (947.6251885357224, 286.06146305352667),
                                           (947.0009213920638, 289.4949323436487),
                                           (946.3766542484053, 292.92840163377076), (946, 295),
                                           (945.6477308422012, 296.3386227996355),
                                           (944.7596104528606, 299.71348027913),
                                           (943.8714900635199, 303.0883377586245),
                                           (942.9833696741792, 306.463195238119),
                                           (942.0952492848386, 309.8380527176135),
                                           (941.2071288954979, 313.212910197108), (941, 314),
                                           (940.3105277278057, 316.5855210207287),
                                           (939.4113470649673, 319.95744850637254),
                                           (938.512166402129, 323.32937599201637),
                                           (937.6129857392906, 326.7013034776602),
                                           (936.7138050764522, 330.073230963304),
                                           (935.8146244136138, 333.44515844894784),
                                           (934.9154437507755, 336.81708593459166),
                                           (934.0162630879372, 340.1890134202355),
                                           (933.1170824250988, 343.5609409058793), (933, 344),
                                           (932.1876052126543, 346.9246212344446),
                                           (931.2535925169049, 350.2870669391425),
                                           (930.3195798211555, 353.6495126438404),
                                           (929.385567125406, 357.0119583485383),
                                           (928.4515544296567, 360.3744040532362), (928, 362),
                                           (927.4299637678045, 363.7101086965867),
                                           (926.3264049414222, 367.0207851757336),
                                           (925.2228461150399, 370.33146165488046),
                                           (924.1192872886576, 373.64213813402733),
                                           (923.0157284622753, 376.9528146131742), (922, 380),
                                           (921.9356687886576, 380.2701910876379),
                                           (921.12736887085, 383.66505074242997),
                                           (920.3190689530423, 387.05991039722204),
                                           (919.5107690352347, 390.4547700520141),
                                           (918.7024691174271, 393.8496297068062),
                                           (917.8941691996195, 397.24448936159826),
                                           (917.0858692818118, 400.6393490163903), (917, 401),
                                           (916.6734853497742, 404.1018891771454),
                                           (916.3081606365209, 407.57247395305114),
                                           (915.9428359232677, 411.0430587289569),
                                           (915.5775112100144, 414.51364350486267),
                                           (915.2121864967612, 417.98422828076843), (915, 420),
                                           (914.818555694359, 421.4515544451279),
                                           (914.3857043105036, 424.9143655159715),
                                           (913.9528529266481, 428.3771765868151),
                                           (913.5200015427927, 431.8399876576587),
                                           (913.0871501589372, 435.3027987285023), (913, 436),
                                           (912.7476648907304, 438.77568620196485),
                                           (912.4317169178286, 442.2511139038861),
                                           (912.1157689449266, 445.72654160580737), (912, 447),
                                           (911.6873103623265, 449.1888274637147),
                                           (911.1937838517343, 452.64351303785963), (911, 454),
                                           (910.5843317207863, 456.07834139606865), (910, 459),
                                           (910, 459.5102405766499), (910, 461), (909, 461), (909, 462)]))
        self.templates.append(GestureTemplate('Swipe up',
                                              [(827, 471), (827, 468), (826.8351614664429, 467.3406458657714),
                                               (826, 464),
                                               (825.9611709740004, 463.7670258440023),
                                               (825.3562407853402, 460.13744471204154),
                                               (825, 458), (824.7033314777157, 456.51665738857855), (824, 453),
                                               (823.989691685753, 452.90722517177693),
                                               (823.5833426869091, 449.25008418218187),
                                               (823.1769936880652, 445.5929431925868), (823, 444),
                                               (823, 441.9230993274217),
                                               (823, 438.24345264239366), (823, 436),
                                               (822.8101872525529, 434.5764043941466),
                                               (822.323871458039, 430.92903593529246),
                                               (821.8375556635251, 427.2816674764383),
                                               (821.3512398690112, 423.63429901758417), (821, 421),
                                               (820.9433077077961, 419.97953874032856),
                                               (820.7391976339736, 416.3055574115243),
                                               (820.5350875601512, 412.6315760827201),
                                               (820.3309774863287, 408.9575947539158),
                                               (820.1268674125063, 405.2836134251116), (820, 403),
                                               (820, 401.6074881198547),
                                               (820, 397.92784143482663), (820, 394.2481947497986),
                                               (820, 390.56854806477054),
                                               (820, 386.8889013797425), (820, 386), (820, 383.20925469471445),
                                               (820, 379.5296080096864), (820, 375.84996132465835), (820, 373),
                                               (820, 372.1703146396303), (820, 368.49066795460226),
                                               (820, 364.8110212695742),
                                               (820, 361.13137458454617), (820, 357.4517278995181),
                                               (820, 353.7720812144901),
                                               (820, 353), (820, 350.092434529462), (820, 346.412787844434),
                                               (820, 342.73314115940593), (820, 339.0534944743779), (820, 338),
                                               (820, 335.37384778934984), (820, 331.6942011043218),
                                               (820, 328.01455441929375),
                                               (820, 325), (820, 324.3349077342657), (820, 320.65526104923765),
                                               (820, 316.9756143642096), (820, 313.29596767918156), (820, 311),
                                               (819.9014169527032, 309.6198373378453),
                                               (819.6392529813972, 305.94954173956074),
                                               (819.3770890100911, 302.2792461412762),
                                               (819.1149250387851, 298.60895054299164),
                                               (819, 297), (819, 294.9334031016595), (819, 291.25375641663146),
                                               (819, 287.5741097316034), (819, 285), (819, 283.89446304657537),
                                               (819, 280.2148163615473), (819, 277), (819, 276.5351696765193),
                                               (819, 272.8555229914912), (819, 269.1758763064632), (819, 269),
                                               (819, 265.49622962143513), (819, 261.8165829364071), (819, 260),
                                               (819.3653768618956, 258.173115690522), (820, 255),
                                               (820, 254.55630907994382),
                                               (820, 252), (820.3552305413385, 250.93430837598453), (821, 249),
                                               (821, 247.3592933700561), (821, 246), (821, 244),
                                               (821, 243.67964668502805),
                                               (821, 243), (821, 242), (822, 242), (822, 241)]))
        self.templates.append(
            GestureTemplate('Swipe left', [(1071, 339), (1070, 339), (1065.3359977715754, 339), (1064, 339),
                                           (1059.6719955431508, 339), (1059, 339),
                                           (1054.05816550956, 338.2940236442229), (1052, 338),
                                           (1048.415058898167, 338), (1042.7510566697424, 338), (1041, 338),
                                           (1037.0870544413178, 338), (1031.4230522128933, 338),
                                           (1025.7590499844687, 338), (1024, 338), (1020.0950477560441, 338),
                                           (1014.4310455276195, 338), (1008.7670432991949, 338), (1004, 338),
                                           (1003.1049019834164, 338.0577482591344),
                                           (997.4526508096178, 338.42240962518594),
                                           (991.8003996358192, 338.78707099123744),
                                           (986.1481484620206, 339.15173235728895),
                                           (980.495897288222, 339.5163937233405),
                                           (974.8436461144233, 339.881055089392), (973, 340),
                                           (969.1857438514685, 340.1315260740873),
                                           (963.5251060440288, 340.3267204812404),
                                           (957.8644682365891, 340.5219148883935),
                                           (952.2038304291494, 340.7171092955466),
                                           (946.5431926217097, 340.91230370269966), (944, 341),
                                           (940.886776537354, 341.19457646641536),
                                           (935.233804508742, 341.5478872182036),
                                           (929.58083248013, 341.90119796999187),
                                           (923.927860451518, 342.2545087217801),
                                           (918.274888422906, 342.6078194735684),
                                           (912.621916394294, 342.9611302253566), (912, 343),
                                           (906.9668888253633, 343.2796172874798),
                                           (901.3116071598142, 343.59379960223254),
                                           (895.6563254942652, 343.90798191698525),
                                           (890.0010438287161, 344.22216423173796),
                                           (884.345762163167, 344.5363465464907),
                                           (878.690480497618, 344.85052886124345), (876, 345),
                                           (873.0306270465192, 345), (867.3666248180946, 345),
                                           (861.70262258967, 345), (856.0386203612454, 345),
                                           (850.3746181328208, 345), (849, 345), (844.7106159043963, 345),
                                           (839.0466136759717, 345), (833.3826114475471, 345),
                                           (827.7186092191225, 345), (822.054606990698, 345), (820, 345),
                                           (816.3906047622734, 345), (810.7266025338488, 345),
                                           (805.0626003054242, 345), (799.3985980769996, 345),
                                           (793.734595848575, 345), (789, 345), (788.0705936201505, 345),
                                           (782.4065913917259, 345), (776.7425891633013, 345),
                                           (771.0785869348767, 345), (765.4145847064522, 345), (761, 345),
                                           (759.7505824780276, 345), (754.086580249603, 345),
                                           (748.4225780211784, 345), (742.7585757927538, 345), (740, 345),
                                           (737.1283587413772, 345.44179096286507),
                                           (731.5302192433722, 346.30304319332737), (727, 347),
                                           (725.9517761098908, 347.2620559725273),
                                           (720.4568868271782, 348.6357782932054), (719, 349), (716, 350),
                                           (715.0000000000005, 350), (715, 350)]))
        self.templates.append(GestureTemplate('Swipe right',
                                              [(672, 380), (673, 380), (675, 380), (678, 380), (678.6206227180982, 380),
                                               (684, 380), (685.2287702910718, 380.17553861301025), (691, 381),
                                               (691.7908003424291, 381), (698.4114230605272, 381), (703, 381),
                                               (705.0320457786254, 381), (711.6526684967235, 381),
                                               (718.2732912148217, 381),
                                               (724.8939139329199, 381), (731.514536651018, 381), (735, 381),
                                               (738.1339162448131, 381.0882793308398),
                                               (744.7519138150213, 381.2747017976062),
                                               (751.3699113852296, 381.46112426437264),
                                               (757.9879089554378, 381.6475467311391),
                                               (764.605906525646, 381.8339691979055),
                                               (771.2239040958542, 382.02039166467193),
                                               (777.8419016660624, 382.20681413143836),
                                               (784.4598992362706, 382.3932365982048),
                                               (791.0778968064789, 382.5796590649712),
                                               (797.6958943766871, 382.76608153173765),
                                               (804.3138919468953, 382.9525039985041), (806, 383),
                                               (810.9338458398767, 383),
                                               (817.5544685579748, 383), (824.175091276073, 383),
                                               (830.7957139941711, 383),
                                               (837.4163367122693, 383), (844.0369594303675, 383), (845, 383),
                                               (850.6575821484656, 383), (857.2782048665638, 383),
                                               (863.898827584662, 383),
                                               (870.5194503027601, 383), (877.1400730208583, 383),
                                               (883.7606957389564, 383),
                                               (890.3813184570546, 383), (892, 383), (897.0019411751528, 383),
                                               (903.6225638932509, 383), (910.2431866113491, 383),
                                               (916.8638093294472, 383),
                                               (923.4844320475454, 383), (930.1050547656436, 383),
                                               (936.7256774837417, 383),
                                               (940, 383), (943.3463002018399, 383), (949.966922919938, 383),
                                               (956.5875456380362, 383), (963.2081683561344, 383),
                                               (969.8287910742325, 383),
                                               (976.4494137923307, 383), (983.0700365104288, 383),
                                               (989.690659228527, 383),
                                               (991, 383), (996.3112819466252, 383), (1002.9319046647233, 383),
                                               (1009.5525273828215, 383), (1016.1731501009197, 383), (1019, 383),
                                               (1022.7937728190178, 383), (1029.414395537116, 383),
                                               (1036.0350182552143, 383),
                                               (1041, 383), (1042.6556409733125, 383), (1049.2762636914108, 383),
                                               (1052, 383),
                                               (1055.896886409509, 383), (1062, 383), (1062.5175091276074, 383),
                                               (1069, 383),
                                               (1069.1381318457056, 383), (1075, 383), (1075.758754563804, 383),
                                               (1082.3793772819022, 383), (1083, 383), (1085, 383), (1087, 383),
                                               (1088, 383),
                                               (1089, 383)]))
        self.templates.append(GestureTemplate('Circle clockwise',
                                              [(906, 263), (906, 262), (907, 262), (909, 261), (912, 261), (916, 260),
                                               (916.1858488780565, 260), (922, 260),
                                               (927.6866168640564, 259.28917289199296),
                                               (930, 259), (937, 259), (939.213636092106, 259), (946, 259),
                                               (950.75865857328, 259), (958, 259),
                                               (962.2888150996549, 259.35740125830455),
                                               (970, 260), (973.5853140666602, 261.2804693095215), (984, 265),
                                               (984.4413251814685, 265.2036885452932),
                                               (994.9237366875192, 270.04172462500884),
                                               (997, 271), (1004.7033600820762, 276.13557338805083), (1009, 279),
                                               (1013.6888571770066, 283.3281758556985), (1022, 291),
                                               (1022.1299775925502, 291.1949663888253),
                                               (1028.534003828282, 300.8010057424232),
                                               (1030, 303), (1033.9811671144928, 310.9623342289856), (1036, 315),
                                               (1037.6284717929434, 321.8395815303619),
                                               (1040.302535987793, 333.07065114873024), (1041, 336),
                                               (1042.1278570008842, 344.45892750663194), (1043, 351),
                                               (1043, 355.94606326214534), (1043, 364),
                                               (1042.6345364412266, 367.47190380834724),
                                               (1041.425948250529, 378.953491619975),
                                               (1041, 383), (1039.287665860244, 390.277420093963), (1037, 400),
                                               (1036.6223888114696, 401.5104447541213), (1034, 412),
                                               (1033.6365105443565, 412.6361065473761), (1030, 419),
                                               (1027.9085753472411, 422.6599931423281), (1026, 426),
                                               (1021.9654110769166, 432.5562070000106), (1018, 439),
                                               (1015.4528017607607, 442.0566378870871), (1013, 445), (1009, 448),
                                               (1006.6988517472912, 449.438217657943), (1001, 453),
                                               (996.684688437534, 455.157655781233), (993, 457), (987, 459),
                                               (985.9455671164626, 459.3163298650612), (977, 462),
                                               (974.816590935816, 462.3119155805977), (970, 463),
                                               (963.372049269745, 463.8284938412819), (962, 464), (954, 465),
                                               (951.912806512975, 465.2319103874472), (945, 466),
                                               (940.4103247810941, 466),
                                               (932, 466), (928.8653022999201, 466), (919, 466),
                                               (917.3332508250724, 465.79165635313404), (911, 465),
                                               (906.0361471257303, 463.5817563216372), (897, 461),
                                               (894.950456962737, 460.3595178008553),
                                               (883.9309641584921, 456.9159262995288),
                                               (881, 456), (872.8243232084005, 453.7702699659274), (870, 453),
                                               (861.9012867593004, 450.0550133670184), (859, 449),
                                               (851.4350521982394, 445.2175260991197), (849, 444),
                                               (841.2877025354325, 439.7153902974625), (840, 439), (833, 433),
                                               (832.4543073029498, 432.34516876353973), (828, 427),
                                               (825.4554947652307, 423.1832421478461), (824, 421),
                                               (821.1789030135025, 412.5367090405073), (821, 412), (818, 403),
                                               (818, 401.50755150226667), (818, 394), (818, 389.9625290210927),
                                               (818, 384),
                                               (818, 378.4175065399187), (818, 375), (819, 367),
                                               (819.007206561837, 366.9351409434661), (820, 358),
                                               (820.7018837833081, 355.5434067584218),
                                               (823.8735453809368, 344.4425911667213),
                                               (824, 344), (827, 334), (827.2037816662928, 333.38865500112144),
                                               (830, 325),
                                               (831.6215622269232, 322.8379170307691), (836, 317),
                                               (837.8995961819828, 313.2008076360344), (839, 311), (844, 305),
                                               (844.9523452657609, 304.1534708748792), (853, 297),
                                               (853.6470214192937, 296.56865238713755), (859, 293),
                                               (863.5719029560305, 290.71404852198475), (865, 290),
                                               (874.2368217158394, 286.3052713136642), (875, 286), (883, 282),
                                               (884.6875011572455, 281.43749961425146), (886, 281), (891, 280),
                                               (896.0234144024183, 279.3720731996977), (899, 279),
                                               (907.4074364312348, 277.47137519432096), (910, 277), (916, 277),
                                               (918.909955037652, 277), (921, 277), (926, 277), (930, 277),
                                               (930.454977518826, 277), (933, 277), (936, 277), (938, 277), (940, 277),
                                               (942, 277)]))
        self.templates.append(GestureTemplate('Circle counterclockwise',
                                              [(931, 287), (930, 286), (928, 286), (925, 286), (923, 286),
                                               (919.1295009954639, 286), (919, 286), (916, 286), (913, 286), (908, 286),
                                               (906.8447884285547, 286), (901, 286),
                                               (894.5920359802063, 286.64079640197934),
                                               (891, 287), (882.493696914654, 288.7012606170692), (881, 289),
                                               (870.5598749088518, 291.61003127278707), (869, 292),
                                               (858.7339719682661, 294.9331508662097), (855, 296),
                                               (847.6245156418934, 300.02299146805814), (844, 302),
                                               (837.0062263159398, 306.19626421043614), (834, 308),
                                               (827.0970053784023, 313.4237814883982), (820, 319),
                                               (818.1921770828338, 321.7117343757493), (812, 331),
                                               (811.3161444002865, 331.88901227962754),
                                               (803.8260229542965, 341.62617015941447), (802, 344),
                                               (797.1312333177967, 351.9117458585803), (794, 357),
                                               (791.0305000993642, 362.5678123136921), (786, 372),
                                               (785.3865769785538, 373.47221525147097), (781, 384),
                                               (780.6066253658116, 384.7867492683768),
                                               (775.1127348890807, 395.7745302218387),
                                               (775, 396), (772.081658636944, 407.673365452224), (772, 408), (772, 419),
                                               (772, 419.9480253815451), (772, 432.23273794845426), (772, 433),
                                               (774, 443),
                                               (774.7083596921208, 444.113136659047), (781, 454),
                                               (781.3327400485518, 454.45751756675884),
                                               (788.5582602944808, 464.3926079049111),
                                               (789, 465), (796.6625558479291, 473.6203753289202), (797, 474),
                                               (803, 479),
                                               (806.249517969559, 481.2746625786912), (813, 486),
                                               (816.6176888841032, 487.8088444420516), (825, 492),
                                               (827.5573131706823, 493.3948980930994), (836, 498),
                                               (838.4222107506789, 499.1179434233903), (849, 504),
                                               (849.6237737587578, 504.1169575797671),
                                               (861.6980760652553, 506.38088926223537),
                                               (865, 507), (873.8265025587928, 508.3239753838189), (885, 510),
                                               (885.9862125079319, 510), (898.2709250748411, 510), (908, 510),
                                               (910.551702862447, 509.85823872986407),
                                               (922.81750131103, 509.17680548272057),
                                               (926, 509), (934.9859823444411, 507.5811606824567), (945, 506),
                                               (947.0955172157227, 505.5343295076172),
                                               (959.0876946616186, 502.86940118630696),
                                               (963, 502), (970.9109552548925, 499.56585992157153), (976, 498),
                                               (982.2977310573775, 495.03636185535174), (993, 490),
                                               (993.3799403904085, 489.74670640639437),
                                               (1003.6014390975611, 482.9323739349593), (1005, 482), (1013, 476),
                                               (1013.4544446048782, 475.6023609707316), (1021, 469),
                                               (1022.763528413739, 467.5891772690088), (1026, 465), (1030, 460),
                                               (1030.8435046588415, 458.48169161408543), (1035, 451),
                                               (1035.730721820914, 447.3463908954302), (1036, 446), (1036, 444),
                                               (1037, 439),
                                               (1037, 435.1873616364281), (1037, 427), (1037, 422.90264906951893),
                                               (1037, 418),
                                               (1035.3986055858647, 410.79372513639134), (1035, 409),
                                               (1030.3278559900098, 399.65571198001965), (1030, 399), (1026, 390),
                                               (1025.3084491546583, 388.44401059798116), (1022, 381),
                                               (1019.5168392501598, 377.6891190002131), (1016, 373),
                                               (1012.436986565492, 367.65547984823803), (1008, 361),
                                               (1005.4285072309824, 357.5713429746432), (999, 349),
                                               (997.96579622388, 347.81805282729147), (992, 341),
                                               (989.4542596879342, 339.0199797572821), (983, 334),
                                               (979.9083705973055, 331.29482427264236), (975, 327),
                                               (970.6246884109122, 323.249732923639), (968, 321), (965, 319),
                                               (960.9221137109172, 315.7376909687337), (960, 315), (952, 309),
                                               (951.0416064461429, 308.4523465406531), (945, 305), (941, 303),
                                               (940.1896824454693, 302.72989414848973), (935, 301), (930, 300),
                                               (928.2847125669089, 300), (926, 300), (923, 300), (922, 300), (920, 300),
                                               (918, 300), (917, 300), (916, 300)]))

    def AddTemplate(self, points, name="newGesture"):
        new_gesture = GestureTemplate(name, points)
        self.templates.append(new_gesture)  # append new template
        num = 0
        for temp in self.templates:
            if temp.Name == name:
                num = num + 1
        print(new_gesture.Points)
        return self.templates[-1]

    # The $1 Gesture Recognizer API begins here -- 3 methods
    def dollar_recognize(self, points):
        points = dollar_resample(points, NumPoints)
        points = rotate_to_zero(points)
        points = scale_to_square(points, SquareSize)
        points = TranslateToOrigin(points)

        b = float('infinity')
        for temp in self.templates:
            d = DistanceAtBestAngle(points, temp, -AngleRange, +AngleRange, AnglePrecision)
            if d < b:
                b = d
                t = temp

        score = 1.0 - (b / HalfDiagonal)
        return (temp.Name, score)
        # return RecogResult(temp.Name, score)


# Helper functions from this point down
def dollar_resample(points, n):
    I = PathLength(points) / (n - 1)  # interval length
    D = 0.0
    # print("X")
    print(points)
    newpoints = [points[0]]
    for i in range(1, len(points)):
        d = Distance(points[i - 1], points[i])
        if (D + d) >= I:
            qx = points[i - 1][0] + ((I - D) / d) * (points[i][0] - points[i - 1][0])
            qy = points[i - 1][1] + ((I - D) / d) * (points[i][1] - points[i - 1][1])
            q = (qx, qy)
            newpoints.append(q)  # append new point 'q'
            points.insert(i, q)  # insert 'q' at position i in points s.t. 'q' will be the next i
            D = 0.0
        else:
            D += d

    # somtimes we fall a rounding-error short of adding the last point, so add it if so
    if len(newpoints) == n - 1:
        newpoints.append(points[-1])
    return newpoints


def rotate_to_zero(points):
    c = centroid(points)
    theta = math.atan2(c[1] - points[0][1], c[0] - points[0][0])
    return rotate_by(points, -theta)


def rotate_by(points, theta):
    c = centroid(points)
    cos = math.cos(theta)
    sin = math.sin(theta)

    newpoints = []
    for p in points:
        qx = (p[0] - c[0]) * cos - (p[1] - c[1]) * sin + c[0]
        qy = (p[0] - c[0]) * sin + (p[1] - c[1]) * cos + c[1]
        newpoints.append((qx, qy))
    return newpoints


def scale_to_square(points, size):
    bb = bounding_box(points)
    newpoints = []
    for p in points:
        qx = p[0] * (size / bb[1][0])
        qy = p[1] * (size / bb[1][1])
        newpoints.append((qx, qy))
    return newpoints


def TranslateToOrigin(points):
    c = centroid(points)
    newpoints = []
    for p in points:
        qx = p[0] - c[0]
        qy = p[1] - c[1]
        newpoints.append((qx, qy))
    return newpoints


def DistanceAtBestAngle(points, T, a, b, threshold):
    x1 = Phi * a + (1.0 - Phi) * b
    f1 = DistanceAtAngle(points, T, x1)
    x2 = (1.0 - Phi) * a + Phi * b
    f2 = DistanceAtAngle(points, T, x2)
    while abs(b - a) > threshold:
        if f1 < f2:
            b = x2
            x2 = x1
            f2 = f1
            x1 = Phi * a + (1.0 - Phi) * b
            f1 = DistanceAtAngle(points, T, x1)
        else:
            a = x1
            x1 = x2
            f1 = f2
            x2 = (1.0 - Phi) * a + Phi * b
            f2 = DistanceAtAngle(points, T, x2)

    return min(f1, f2)


def DistanceAtAngle(points, T, theta):
    newpoints = rotate_by(points, theta)
    newlist = newpoints[:len(T.Points)]
    return PathDistance(newlist, T.Points)


def centroid(points):
    x = 0.0
    y = 0.0
    for p in points:
        x += p[0]
        y += p[1]

    x /= len(points)
    y /= len(points)
    return (x, y)


def bounding_box(points):
    minX = float('infinity')
    maxX = float('-infinity')
    minY = float('infinity')
    maxY = float('-infinity')

    for p in points:
        if (p[0] < minX):
            minX = p[0]
        if (p[0] > maxX):
            maxX = p[0]
        if (p[1] < minY):
            minY = p[1]
        if (p[1] > maxY):
            maxY = p[1]

    # return [(X,Y),(width,height)]
    return [(minX, minY), (maxX - minX, maxY - minY)]


def PathDistance(pts1, pts2):
    d = 0.0
    print(len(pts1))
    print(len(pts2))
    for i in range(0, len(pts1)):  # assumes pts1.length == pts2.length
        d += Distance(pts1[i], pts2[i])
    return d / len(pts1)


def PathLength(points):
    d = 0.0
    for i in range(1, len(points)):
        d += Distance(points[i - 1], points[i])
    return d


def Distance(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)
