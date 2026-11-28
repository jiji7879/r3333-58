import K58.Arm
import K58.Attachment
import K58.PhysicalBridge
import K58.Corollaries
import K58.ExchangeResidue
import K58.Link14
import K58.M7
import K58.Design
import K58.Model
import K58.Selection
import K58.Ticket
import K58.Interface
import K58.Blocked
import K58.Templates
import K58.TwoArm
import K58.Classification
import K58.MarkedPalette
import K58.KindPlan
import K58.MarkBreadth
import K58.Ledger
import K58.EmbeddingCover
import K58.RawCover
import K58.FamilyGluing
import K58.StructuralTransport
import K58.TransportExample
import K58.BulkReplay
import K58.RootMasks
import K58.ArmRung
import K58.ArmFarFive
import K58.ArmFarFourReg
import K58.ArmSender
import K58.SomeSix
import K58.ZeroSet
import K58.Multiplicity
import K58.CountLaw
import K58.Weighted
import K58.Codegree
import K58.ForcedPentagon
import K58.NoSingleton
import K58.DesignIncidence
import K58.Incidence
import K58.ProfilesIncidence
import K58.ArmLayer
import K58.PlacementsIneq
import K58.SixCycle
import K58.PBRoot
import K58.LinkSaturation
import K58.FullVertexBudget
import K58.EncoderExtensions
import K58.ConfigurableMaximal
import K58.TargetParent
import K58.SenderReady
import K58.SupportCatalogue
import K58.SupportTransport
import K58.EmittedBridge
import K58.TargetUnits
import K58.TicketPremises

#print axioms K58.sum_w_eq_sum_H
#print axioms K58.exists_root
#print axioms K58.sum_deg
#print axioms K58.deg_le_two_of_two_colour
#print axioms K58.two_colour_six
#print axioms K58.three_colour_seventeen
#print axioms K58.deg_le_sixteen
#print axioms K58.template_triangleFree_15
#print axioms K58.template_triangleFree_16
#print axioms K58.card_filter_colour
#print axioms K58.w_eq_sum_critical
#print axioms K58.H_eq_sum_armSenders
#print axioms K58.threshold_pigeonhole
#print axioms K58.profile_sum
#print axioms K58.exists_arm_reaches
#print axioms K58.plans_ok_bool
#print axioms K58.plans_ok
#print axioms K58.plans_feasible_bool
#print axioms K58.plans_feasible
#print axioms K58.original_threshold_hypothesis_impossible
#print axioms K58.balanced_root_arm_reaches
#print axioms K58.exists_balanced_root_arm_reaches
#print axioms K58.sorted_degree_profile_mem
#print axioms K58.root_degree_profile
#print axioms K58.planned_degree_profiles
#print axioms K58.indexed_plans_ok
#print axioms K58.arm_senders_le_deg
#print axioms K58.normalized_plan_arm_reaches
#print axioms K58.exists_plan_matching
#print axioms K58.exists_plan_arm_reaches
#print axioms K58.root_plan_arm
#print axioms K58.mixture
#print axioms K58.mixture_subset
#print axioms K58.arm_part_le_five
#print axioms K58.nbr_indep
#print axioms K58.interface_count
#print axioms K58.arm_degree_sum_fourteen
#print axioms K58.model_pair_disjoint
#print axioms K58.model_pair_rigidity
#print axioms K58.light_count_parity
#print axioms K58.sum_inter_nbr_even
#print axioms K58.TwoArm.two_arm_restriction
#print axioms K58.TwoArm.coverage_le
#print axioms K58.TwoArm.exact_degree
#print axioms K58.uniform_branch_zero_critical
#print axioms K58.ten_outside
#print axioms K58.crit_card_ge_thirty
#print axioms K58.crit_eq_univ
#print axioms K58.armFar_le_five
#print axioms K58.armFar_le_two
#print axioms K58.armFar_eq_empty
#print axioms K58.indep_le_sixteen
#print axioms K58.interface
#print axioms K58.blocked_set_le_five
#print axioms K58.part_family_le_five
#print axioms K58.M_ge_seven
#print axioms K58.M_ge_six
#print axioms K58.rigid_six
#print axioms K58.arm_codeg_le_five
#print axioms K58.arm_all_five
#print axioms K58.arm_pair_total
#print axioms K58.rx_bound
#print axioms K58.collision_engine
#print axioms K58.pair_filter_le
#print axioms K58.branch_crit
#print axioms K58.branch_deg_15_or_16
#print axioms K58.codeg_le_sixteen
#print axioms K58.Residue.residue_pattern
#print axioms K58.Residue.residue_forced
#print axioms K58.Residue.residue_two_way
#print axioms K58.Residue.exists_complement
#print axioms K58.Residue.exchange_sixteen
#print axioms K58.Residue.exchange_fifteen
#print axioms K58.Residue.residue_arms
#print axioms K58.le_choose_two_add_one
#print axioms K58.collision_engine_add_one
#print axioms K58.rx_lower_refined
#print axioms K58.design_forces_light
#print axioms K58.trace_codegree_six
#print axioms K58.design_not_realisable
#print axioms K58.classified_15
#print axioms K58.classified_16
#print axioms K58.no_marked_swap_15
#print axioms K58.catalogue_col_15
#print axioms K58.catalogue_col_16
#print axioms K58.palette_15
#print axioms K58.palette_16_fixing
#print axioms K58.marked_sender
#print axioms K58.pin_of_named_classification
#print axioms K58.template_support_shape
#print axioms K58.pinned_support_shape
#print axioms K58.critical_arm_pinned
#print axioms K58.marked_sender_pinned
#print axioms K58.PositionSearch.mem_automorphisms_iff
#print axioms K58.named15_exact
#print axioms K58.mem_positionOrbit15
#print axioms K58.positionOrbit16_all
#print axioms K58.markClasses15_TTT
#print axioms K58.markClasses15_UUU
#print axioms K58.ledger_mark_breadth
#print axioms K58.reached15_has_retained_mark
#print axioms K58.root_plan_with_kinds
#print axioms K58.frozenKeys_length
#print axioms K58.template15_zero_degrees
#print axioms K58.named_position_counts15
#print axioms K58.support_embedding_represented
#print axioms K58.pin_in_global_palette
#print axioms K58.root_plan_in_global_palette
#print axioms K58.slotLabel_bijective
#print axioms K58.slotLabel_val
#print axioms K58.exists_root_layout
#print axioms K58.attached_block_realizes
#print axioms K58.frozenCover_of_attachments
#print axioms K58.reached_layout_sender
#print axioms K58.root_layout_marked_block
#print axioms K58.realizes_of_unitTransport
#print axioms K58.frozenCover_of_rawCover
#print axioms K58.secondRoots15_exact
#print axioms K58.rawFamilies_length
#print axioms K58.marked_orbit_lifts
#print axioms K58.root_layout_at_retained_mark
#print axioms K58.canonicalArm_ok
#print axioms K58.exists_realized_raw_family
#print axioms K58.rawCover_of_family_placements
#print axioms K58.frozenCover_of_family_placements
#print axioms K58.familyPlacementCover
#print axioms K58.rawCover
#print axioms K58.named16_exact
#print axioms K58.supportTable_cover
#print axioms K58.expandKey_of_labels
#print axioms K58.Frozen.Address.mem
#print axioms K58.transport_of_bits
#print axioms K58.covered_of_transportCheck
#print axioms K58.cover_family_of_grid
#print axioms K58.PlacementTables.expand_exact
#print axioms K58.transport_of_alignment
#print axioms K58.covered_aligned
#print axioms K58.PlacementTables.expand_marking
#print axioms K58.rawTransportCover_of_plans
#print axioms K58.frozenCover_of_transports
#print axioms K58.example_transport_into_frozen
#print axioms K58.grid_of_checked_rows
#print axioms K58.root_of_packed_test
#print axioms K58.mem_nbrC_swap
#print axioms K58.sum_inter_nbrC_comm
#print axioms K58.word_support_eq_five
#print axioms K58.sum_support_arm
#print axioms K58.sum_support_subset
#print axioms K58.rung_guard
#print axioms K58.rung_exists_le_eight
#print axioms K58.guard_sharp
#print axioms K58.block_le_five
#print axioms K58.block_le_five_subset
#print axioms K58.block_le_ten
#print axioms K58.exists_class_of_ne
#print axioms K58.nbrC_zero_cover
#print axioms K58.nbrC_zero_card_split
#print axioms K58.rung_box
#print axioms K58.rung_three_slack
#print axioms K58.slack_sharp
#print axioms K58.rung_deficiency
#print axioms K58.arm_triple
#print axioms K58.two_arm_law
#print axioms K58.M_ge_seven_of_crit
#print axioms K58.armFar_five_zero_degree
#print axioms K58.armFar_five_nonzero_degree
#print axioms K58.far18_triangleFree
#print axioms K58.far18X_card
#print axioms K58.far18_X_free
#print axioms K58.far18_armFar_card
#print axioms K58.armFar_four_attained
#print axioms K58.arm_sender_free_of_reciprocal
#print axioms K58.armSenders_eq_zero_of_reciprocal
#print axioms K58.armSenders_le_deg
#print axioms K58.armSenders_eq_of_reciprocal
#print axioms K58.H_eq_w_of_reciprocal
#print axioms K58.arm0_reaches_of_arm_senders_zero
#print axioms K58.arm0_reaches_of_reciprocal
#print axioms K58.not_reciprocal_of_arm_sender
#print axioms K58.interface_count'
#print axioms K58.some_six_count
#print axioms K58.some_six_or_deficit
#print axioms K58.some_six_excess
#print axioms K58.card_le_sixteen_of_zeroFree
#print axioms K58.wordClass_card_le_six
#print axioms K58.wordClass_pair_le
#print axioms K58.card_inter_union_le_two
#print axioms K58.card_inter_union_le_three
#print axioms K58.no_three_pairwise
#print axioms K58.sum_inter_four_ge
#print axioms K58.card_le_three
#print axioms K58.distinct_supports_ge_nine
#print axioms K58.inter_card_le_four
#print axioms K58.inter_card_le_capacity
#print axioms K58.sixfold_disjoint
#print axioms K58.two_fivefold_at_point
#print axioms K58.sender_union_ge_thirteen
#print axioms K58.sender_not_two_supports
#print axioms K58.sixfold_excludes_at_point
#print axioms K58.spec_0_0_0_6_0_3
#print axioms K58.spec_0_0_0_8_2_0
#print axioms K58.spec_0_0_0_9_0_1
#print axioms K58.spec_0_0_1_6_3_0
#print axioms K58.spec_0_0_1_7_1_1
#print axioms K58.spec_0_0_2_5_2_1
#print axioms K58.spec_0_0_2_6_0_2
#print axioms K58.spec_0_0_2_9_0_0
#print axioms K58.spec_0_0_3_4_1_2
#print axioms K58.spec_0_0_3_7_1_0
#print axioms K58.spec_0_0_4_3_0_3
#print axioms K58.spec_0_0_4_5_2_0
#print axioms K58.spec_0_0_4_6_0_1
#print axioms K58.spec_0_0_5_3_3_0
#print axioms K58.spec_0_0_5_4_1_1
#print axioms K58.spec_0_0_6_2_2_1
#print axioms K58.spec_0_0_6_3_0_2
#print axioms K58.spec_0_0_7_1_1_2
#print axioms K58.spec_0_0_8_0_0_3
#print axioms K58.spec_0_1_0_6_2_1
#print axioms K58.spec_0_1_0_7_0_2
#print axioms K58.spec_0_1_0_10_0_0
#print axioms K58.spec_0_1_1_5_1_2
#print axioms K58.spec_0_1_1_8_1_0
#print axioms K58.spec_0_1_2_4_0_3
#print axioms K58.spec_0_1_2_6_2_0
#print axioms K58.spec_0_1_2_7_0_1
#print axioms K58.spec_0_1_3_4_3_0
#print axioms K58.spec_0_1_3_5_1_1
#print axioms K58.spec_0_1_4_3_2_1
#print axioms K58.spec_0_1_4_4_0_2
#print axioms K58.spec_0_1_5_2_1_2
#print axioms K58.spec_0_1_6_1_0_3
#print axioms K58.spec_0_2_0_5_0_3
#print axioms K58.spec_0_2_0_7_2_0
#print axioms K58.spec_0_2_0_8_0_1
#print axioms K58.spec_0_2_1_5_3_0
#print axioms K58.spec_0_2_1_6_1_1
#print axioms K58.spec_0_2_2_4_2_1
#print axioms K58.spec_0_2_2_5_0_2
#print axioms K58.spec_0_2_3_3_1_2
#print axioms K58.spec_0_2_4_2_0_3
#print axioms K58.spec_0_3_0_5_2_1
#print axioms K58.spec_0_3_0_6_0_2
#print axioms K58.spec_0_3_1_4_1_2
#print axioms K58.spec_0_3_2_3_0_3
#print axioms K58.spec_0_4_0_4_0_3
#print axioms K58.spec_1_0_0_6_1_2
#print axioms K58.spec_1_0_0_9_1_0
#print axioms K58.spec_1_0_1_5_0_3
#print axioms K58.spec_1_0_1_7_2_0
#print axioms K58.spec_1_0_1_8_0_1
#print axioms K58.spec_1_0_2_5_3_0
#print axioms K58.spec_1_0_2_6_1_1
#print axioms K58.spec_1_0_3_4_2_1
#print axioms K58.spec_1_0_3_5_0_2
#print axioms K58.spec_1_0_4_3_1_2
#print axioms K58.spec_1_0_5_2_0_3
#print axioms K58.spec_1_1_0_6_3_0
#print axioms K58.spec_1_1_0_7_1_1
#print axioms K58.spec_1_1_1_5_2_1
#print axioms K58.spec_1_1_1_6_0_2
#print axioms K58.spec_1_1_2_4_1_2
#print axioms K58.spec_1_1_3_3_0_3
#print axioms K58.spec_1_2_0_5_1_2
#print axioms K58.spec_1_2_1_4_0_3
#print axioms K58.spec_2_0_0_6_2_1
#print axioms K58.spec_2_0_0_7_0_2
#print axioms K58.spec_2_0_1_5_1_2
#print axioms K58.spec_2_0_2_4_0_3
#print axioms K58.spec_2_1_0_5_0_3
#print axioms K58.law_T_h2_k5
#print axioms K58.law_U_h2_k5
#print axioms K58.law_T_h3_k5
#print axioms K58.law_U_h3_k5
#print axioms K58.law_T_h2_k4
#print axioms K58.law_U_h2_k4
#print axioms K58.law_T_h3_k4
#print axioms K58.law_U_h3_k4
#print axioms K58.templates_agree
#print axioms K58.class_sizes_T
#print axioms K58.class_sizes_U
#print axioms K58.class_size_profile
#print axioms K58.sum_le_of_card_eq
#print axioms K58.nine_of_fourteen
#print axioms K58.not_eight_fives
#print axioms K58.total_le_five
#print axioms K58.codegree_count
#print axioms K58.nine_le_codegree
#print axioms K58.ForcedPentagon.Colouring.card_le_two_of_clique
#print axioms K58.ForcedPentagon.Colouring.degree_two_of_two_colours
#print axioms K58.ForcedPentagon.Colouring.degree_into_four
#print axioms K58.ForcedPentagon.Colouring.endpoint
#print axioms K58.ForcedPentagon.Colouring.eq_two_or_three
#print axioms K58.ForcedPentagon.Colouring.ne_one_of_arm
#print axioms K58.ForcedPentagon.Colouring.ne_zero_of_common_zero
#print axioms K58.ForcedPentagon.Colouring.completion_colour_ne
#print axioms K58.ForcedPentagon.Colouring.two_completions_zero
#print axioms K58.ForcedPentagon.Colouring.at_most_two_completions
#print axioms K58.ForcedPentagon.Colouring.completions_no_common_zero
#print axioms K58.ForcedPentagon.Colouring.triangleFree_noMono
#print axioms K58.ForcedPentagon.Colouring.at_most_two_completions_of_triangleFree
#print axioms K58.ForcedPentagon.Colouring.two_completions_zero_of_triangleFree
#print axioms K58.ForcedPentagon.Colouring.degree_two_of_two_colours_of_triangleFree
#print axioms K58.ForcedPentagon.Colouring.sharpBoard_noMono
#print axioms K58.ForcedPentagon.Colouring.sharp_attained
#print axioms K58.template_class_triple_T
#print axioms K58.template_class_triple_U
#print axioms K58.card_four_of_sum
#print axioms K58.partition_law
#print axioms K58.mcodeg_comm
#print axioms K58.classes_eq_two_of_wt_four
#print axioms K58.mcodeg_le_two_of_four_five
#print axioms K58.codegree_le_ten_of_cross
#print axioms K58.mult_le_five
#print axioms K58.card_large_le_three
#print axioms K58.not_all_even
#print axioms K58.no_design_three_three_three_three_one_one
#print axioms K58.no_design_seven_twos
#print axioms K58.sum_tot
#print axioms K58.disjoint_of_add_gt
#print axioms K58.inc_card_le_three
#print axioms K58.no_four_heavy
#print axioms K58.tot_even
#print axioms K58.excl_all_even
#print axioms K58.no_all_even
#print axioms K58.excl_3333
#print axioms K58.excl_442211
#print axioms K58.inc_mult_le_five
#print axioms K58.excl_2_7
#print axioms K58.excl_4_2_2_2_2_2
#print axioms K58.excl_3_3_3_3_1_1
#print axioms K58.excl_4_4_2_2_1_1
#print axioms K58.arith_key
#print axioms K58.arith_filter
#print axioms K58.x5_redundant
#print axioms K58.profile_allW
#print axioms K58.witnesses
#print axioms K58.count_alternates
#print axioms K58.count_form
#print axioms K58.four_count_vectors
#print axioms K58.alternating_solutions
#print axioms K58.no_triangle_weights
#print axioms K58.count_vector_pairs
#print axioms K58.facts_display16
#print axioms K58.facts_p36_0
#print axioms K58.facts_p36_1
#print axioms K58.facts_p36_2
#print axioms K58.count_vector_display16
#print axioms K58.count_vector_p36_0
#print axioms K58.count_vector_p36_1
#print axioms K58.count_vector_p36_2
#print axioms K58.intra3_distinct
#print axioms K58.case_count
#print axioms K58.image0_facts
#print axioms K58.image1_facts
#print axioms K58.image2_facts
#print axioms K58.image3_facts
#print axioms K58.image_partitions_distinct
#print axioms K58.image0_is_display
#print axioms K58.T_invariant
#print axioms K58.T_values
#print axioms K58.no_iso_display_p36_0
#print axioms K58.no_iso_display_p36_1
#print axioms K58.no_iso_display_p36_2
#print axioms K58.p36_pairwise_inequivalent
#print axioms K58.connected_of_two_regular_of_triangle_free
#print axioms K58.connected_of_weights

-- results/pb-codegree-2026-11-24, ledger #33
#print axioms K58.pb_two_colour_card_le_five
#print axioms K58.pb_card_le_five_of_avoids
#print axioms K58.pb_root_blue_degree

-- Duggan-paper method review, independently accepted finite artifacts.
#print axioms K58.template_alternativeClosed_15
#print axioms K58.template_alternativeClosed_16
#print axioms k58_root_margin
#print axioms k58_total_deficit_lower
#print axioms k3_naive_phi
#print axioms K58.EncoderExtensions.legacy_atLeastCNF_not_native
#print axioms K58.EncoderExtensions.satisfiable_nativeAtLeast
#print axioms K58.EncoderExtensions.satisfiable_guardedAtLeast
#print axioms K58.EncoderExtensions.satisfiable_supportFamily

-- Pure-kernel configurable maximal-colour normal form.
#print axioms K58.ConfigurableMaximal.triangleFree_recolour
#print axioms K58.ConfigurableMaximal.normalAt_normalise
#print axioms K58.ConfigurableMaximal.normalise_suffix
#print axioms K58.ConfigurableMaximal.normalForm_equisatisfiable
#print axioms K58.ConfigurableMaximal.witnessBinding_iff
#print axioms K58.ConfigurableMaximal.fresh_witness_disjunction

-- Exact parent conditional semantic assembly and physical ticket premise.
#print axioms K58.SemanticAssembly.satisfiable_emittedSupportFamily
#print axioms K58.SemanticAssembly.chain_extend
#print axioms targetParent_satisfiable_of_ready
#print axioms K58.SemanticAssembly.seven_critical_senders_of_16_16_14_11
#print axioms K58.SemanticAssembly.six_of_adjusted_guard_count

-- Physical base/unit realization; ChainReady remains an explicit premise.
#print axioms targetBase_varsBelow
#print axioms hostVar_inj_sorted
#print axioms realizedValuation_hostVar
#print axioms hostBase_satisfiable
#print axioms targetUnit_satisfiable_of_expanded
#print axioms targetBase_satisfiable_of_realizesKey
#print axioms targetParent_satisfiable_of_expanded_ready

-- CAT58 and exact attachment bounds; not a wall/profile closure.
#print axioms K58.card_biUnion_ge_union_bound
#print axioms K58.exists_pair_large_inter
#print axioms K58.cat58
#print axioms K58.card_le_five_of_two_colours
#print axioms K58.attachment_bound
#print axioms K58.attachment_colour_ne

-- Finite support catalogue, conditional physical transport, and exact emitted readiness.
#print axioms K58.SupportCatalogue.catalogue_iff
#print axioms K58.SupportCatalogue.p4_complete
#print axioms K58.SupportCatalogue.c5_complete
#print axioms K58.SupportCatalogue.control_indep_not_member
#print axioms K58.SupportTransport.support_mask_mem
#print axioms K58.SupportTransport.support_mask_mem_of_deg
#print axioms K58.SupportTransport.emittedSupportStep_ready_shape
#print axioms K58.SupportTransport.sender18_ready
#print axioms K58.SenderReady.supportAudit_eq
#print axioms K58.SenderReady.supportShapeAudit_eq
#print axioms K58.SenderReady.exists_extension_iff
#print axioms K58.SenderReady.sender_family_ready
#print axioms K58.SenderReady.sender18_ready
#print axioms K58.SenderReady.counter_semantics_not_shape
#print axioms K58.SenderReady.counter_then_support_unsatisfiable
#print axioms K58.SenderReady.coordinate_order_matters

-- Emitted coordinate/physical bridge and retained key units. Counter-to-finset, key bookkeeping, external classification and ChainReady remain separate.
#print axioms K58.EmittedBridge.rowAtoms_val
#print axioms K58.EmittedBridge.rowAtomsList_val
#print axioms K58.EmittedBridge.realized_rowAtoms
#print axioms K58.EmittedBridge.emitted_mask_of_pinned
#print axioms K58.EmittedBridge.emitted_sender_step_ready_of_count
#print axioms K58.EmittedBridge.sender_pinned_of_count
#print axioms K58.EmittedBridge.triangle_free_third_ne
#print axioms K58.EmittedBridge.deg_ge_of_counted
#print axioms K58.TargetUnits.arm0_block_units
#print axioms K58.TargetUnits.arm0_root_units
#print axioms K58.TargetUnits.arm1_root_units
#print axioms K58.TargetUnits.targetUnitCNF_mem
#print axioms K58.TargetUnits.hroot_of_unit_mem
#print axioms K58.TargetUnits.root_edge_colour_of_unit_mem
