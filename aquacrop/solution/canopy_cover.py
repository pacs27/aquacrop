import os
import numpy as np

from ..entities.totalAvailableWater import TAW
from ..entities.moistureDepletion import Dr

from ..entities.waterStressCoefficients import Ksw
from .adjust_CCx import adjust_CCx

if __name__ != "__main__":
    if os.getenv("DEVELOPMENT"):
        from .water_stress import water_stress
        from .root_zone_water import root_zone_water
        from .cc_development import cc_development
        from .update_CCx_CDC import update_CCx_CDC
        from .cc_required_time import cc_required_time
    else:
        from .solution_water_stress import water_stress
        from .solution_root_zone_water import root_zone_water
        from .solution_cc_development import cc_development
        from .solution_update_CCx_CDC import update_CCx_CDC
        from .solution_cc_required_time import cc_required_time
else:
    from .water_stress import water_stress
    from .root_zone_water import root_zone_water
    from .cc_development import cc_development
    from .update_CCx_CDC import update_CCx_CDC
    from .cc_required_time import cc_required_time

from typing import NamedTuple, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Important: classes are only imported when types are checked, not in production.
    from aquacrop.entities.initParamVariables import InitialCondition
    from aquacrop.entities.soilProfile import SoilProfileNT
    from aquacrop.entities.crop import CropStructNT


def canopy_cover(
    crop: "CropStructNT",
    soil_profile: "SoilProfileNT",
    top_soil_depth_zTop: float,
    initialCond: "InitialCondition",
    gdd: float,
    et0: float,
    growing_season: bool,
):
    # def CCCrop,Soil_Profile,top_soil_depth_zTop,initialCond,gdd,et0,growing_season):

    """
    Function to simulate canopy growth/decline

    <a href="https://www.fao.org/3/BR248E/br248e.pdf#page=30" target="_blank">Reference Manual: canopy_cover equations</a> (pg. 21-33)


    Arguments:

        crop (CropStructNT): NamedTuple of crop object

        soil_profile (SoilProfileNT): NamedTuple of SoilProfile object

        top_soil_depth_zTop (float): top soil depth

        initialCond (InitialCondition): initialCond object

        gdd (float): Growing Degree Days

        et0 (float): reference evapotranspiration

        growing_season (bool): is it currently within the growing season (True, Flase)

    Returns:

        NewCond (InitialCondition): updated initialCond object


    """

    # Function to simulate canopy growth/decline

    initial_cc_ns = initialCond.canopy_cover_ns  # initial canopy cover non-stressed
    initial_canopy_cover = initialCond.canopy_cover  # initial canopy cover
    initial_protected_seed = initialCond.protected_seed
    initial_CCxAct = initialCond.ccx_act
    initial_is_crop_dead = initialCond.crop_dead  # Is crop dead? (True, False)
    initial_t_early_sen = initialCond.t_early_sen
    initial_CCxW = initialCond.ccx_w
    initial_canopy_cover_emergence_CC0_adj = initialCond.cc0_adj

    # Values needed
    initial_z_root = float(initialCond.z_root)  # rooting depth [mm]
    initial_th = initialCond.th  # Water content in the root zone (TODO: CHECK this)
    z_min = float(crop.Zmin)  # minimum depth of the root zone [mm]
    aeration_stress = (
        crop.Aer
    )  # Vol (%) below saturation at which stress begins to occur due to deficient aeration
    initial_dap = initialCond.dap  # days after planting
    initial_delayed_cds = (
        initialCond.delayed_cds
    )  # delayed crop development stage (days) TODO: CHECK this
    initial_gdd_cum = initialCond.gdd_cum  # cumulative growing degree days
    initial_delayed_gdds = (
        initialCond.delayed_gdds
    )  # delayed growing degree days (days) TODO: Check this

    initial_protected_seed = initialCond.protected_seed

    initial_CCxAct = initialCond.ccx_act
    initial_is_crop_dead = initialCond.crop_dead  # Is crop dead? (True, False)

    initial_ccx_early_sen = initialCond.ccx_early_sen
    initial_CCxW = initialCond.ccx_w

    ## Store initial conditions in a new structure for updating ##
    NewCond = initialCond
    NewCond.cc_prev = initialCond.canopy_cover

    ## Calculate canopy development (if in growing season) ##
    if growing_season == True:
        (
            canopy_cover,
            canopy_cover_adj,
            canopy_cover_ns,
            canopy_cover_adj_ns,
            ccx_w,
            ccx_act,
            ccx_w_ns,
            ccx_act_ns,
            premat_senes,
            ccx_early_sen,
            t_early_sen,
            cc0_adj,
            is_crop_dead,
            protected_seed,
        ) = calculate_canopy_cover_grow(
            soil_profile=soil_profile,
            z_root=initial_z_root,
            z_min=z_min,
            th=initial_th,
            top_soil_depth_zTop=top_soil_depth_zTop,
            aeration_stress=aeration_stress,
            crop=crop,
            et0=et0,
            initial_dap=initial_dap,
            initial_delayed_cds=initial_delayed_cds,
            gdd=gdd,
            initial_gdd_cum=initial_gdd_cum,
            initial_delayed_gdds=initial_delayed_gdds,
            initial_cc_ns=initial_cc_ns,
            initial_ccx_act_ns=initial_CCxAct,
            initial_canopy_cover=initial_canopy_cover,
            initial_canopy_cover_emergence_CC0_adj=initial_canopy_cover_emergence_CC0_adj,
            initial_t_early_sen=initial_t_early_sen,
            initial_protected_seed=initial_protected_seed,
            initial_CCxAct=initial_CCxAct,
            initial_is_crop_dead=initial_is_crop_dead,
            initial_ccx_early_sen=initial_ccx_early_sen,
            initial_CCxW=initial_CCxW,
        )

        if canopy_cover != None:
            NewCond.canopy_cover = canopy_cover

        if canopy_cover_adj != None:
            NewCond.canopy_cover_adj = canopy_cover_adj

        if canopy_cover_ns != None:
            NewCond.canopy_cover_ns = canopy_cover_ns

        if canopy_cover_adj_ns != None:
            NewCond.canopy_cover_adj_ns = canopy_cover_adj_ns

        if ccx_w != None:
            NewCond.ccx_w = ccx_w

        if ccx_act != None:
            NewCond.ccx_act = ccx_act

        if ccx_w_ns != None:
            NewCond.ccx_w_ns = ccx_w_ns

        if ccx_act_ns != None:
            NewCond.ccx_act_ns = ccx_act_ns

        if premat_senes != None:
            NewCond.premat_senes = premat_senes

        if ccx_early_sen != None:
            NewCond.ccx_early_sen = ccx_early_sen

        if t_early_sen != None:
            NewCond.t_early_sen = t_early_sen

        if cc0_adj != None:
            NewCond.cc0_adj = cc0_adj

        if is_crop_dead != None:
            NewCond.is_crop_dead = is_crop_dead

        if protected_seed != None:
            NewCond.protected_seed = protected_seed

    else:
        # No canopy outside growing season - set various values to zero
        NewCond.canopy_cover = 0
        NewCond.canopy_cover_adj = 0
        NewCond.canopy_cover_ns = 0
        NewCond.canopy_cover_adj_ns = 0
        NewCond.ccx_w = 0
        NewCond.ccx_act = 0
        NewCond.ccx_w_ns = 0
        NewCond.ccx_act_ns = 0

    return NewCond


def calculate_canopy_cover_grow(
    soil_profile,
    z_root,
    th,
    top_soil_depth_zTop,
    z_min,
    aeration_stress,
    crop,
    et0,
    initial_dap,
    initial_delayed_cds,
    gdd,
    initial_gdd_cum,
    initial_delayed_gdds,
    initial_cc_ns,
    initial_ccx_act_ns,
    initial_canopy_cover,
    initial_canopy_cover_emergence_CC0_adj,
    initial_t_early_sen,
    initial_protected_seed,
    initial_CCxAct,
    initial_is_crop_dead,
    initial_ccx_early_sen,
    initial_CCxW,
):
    # variables to be returned
    canopy_cover = None
    canopy_cover_adj = None
    canopy_cover_ns = None
    canopy_cover_adj_ns = None
    ccx_w = None
    ccx_act = None
    ccx_w_ns = None
    ccx_act_ns = None
    premat_senes = None
    ccx_early_sen = None
    t_early_sen = None
    cc0_adj = None
    is_crop_dead = None
    protected_seed = None

    # Parameters needed
    crop_time_to_emergence = crop.Emergence
    crop_time_to_maturity = crop.Maturity
    crop_time_to_canopy_end_development = crop.CanopyDevEnd
    crop_time_to_senescense = crop.Senescence
    canopy_cover_emergence_CC0 = crop.CC0
    maximun_canopy_cover_CCx = crop.CCx
    canopy_growth_coefficient_CGC = crop.CGC
    canopy_decline_coefficient_CDC = crop.CDC

    # Calculate root zone water content
    taw = TAW()
    root_zone_depletion = Dr()

    (
        _,
        root_zone_depletion.Zt,
        root_zone_depletion.Rz,
        taw.Zt,
        taw.Rz,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = root_zone_water(
        soil_profile,
        z_root,
        th,
        top_soil_depth_zTop,
        z_min,
        aeration_stress,
    )

    root_zone_depletion, taw = choose_between_root_zone_or_top_soil_depletions(
        root_zone_depletion=root_zone_depletion, taw=taw
    )

    water_stress_coef = calculate_water_stress(
        crop_p_up=crop.p_up,
        crop_p_lo=crop.p_lo,
        crop_ETadj=crop.ETadj,
        crop_beta=crop.beta,
        crop_fshape_w=crop.fshape_w,
        t_early_sen=initial_t_early_sen,
        root_zone_depletion=root_zone_depletion,
        taw=taw,
        et0=et0,
        beta=True,
    )

    calendar_type = crop.CalendarType

    (
        time_delta_of_canopy_growth,
        time_canopy_cover_adjusted,
    ) = get_canopy_cover_growth_time(
        calendar_type=calendar_type,
        dap=initial_dap,
        delayed_cds=initial_delayed_cds,
        gdd=gdd,
        gdd_cum=initial_gdd_cum,
        delayed_gdds=initial_delayed_gdds,
    )

    ## Canopy development (potential) ##
    (canopy_cover_ns_pcc, cc0_adj_pcc, ccx_w_ns_pcc, ccx_act_ns_pcc) = calculate_potential_canopy_cover(
        time_canopy_cover_adjusted,
        crop_time_to_emergence,
        crop_time_to_maturity,
        crop_time_to_canopy_end_development,
        crop_time_to_senescense,
        initial_cc_ns,
        canopy_cover_emergence_CC0,
        maximun_canopy_cover_CCx,
        canopy_growth_coefficient_CGC,
        canopy_decline_coefficient_CDC,
        time_delta_of_canopy_growth,
        initial_ccx_act_ns,
    )
    
    if canopy_cover_ns_pcc != None:
        canopy_cover_ns = canopy_cover_ns_pcc
    if cc0_adj_pcc != None:
        cc0_adj = cc0_adj_pcc
    if ccx_w_ns_pcc != None:
        ccx_w_ns = ccx_w_ns_pcc
    if ccx_act_ns_pcc != None:
        ccx_act_ns = ccx_act_ns_pcc

    (
        canopy_cover_ac,
        cc0_adj_ac,
        ccx_act_ac,
        is_crop_dead_ac,
        protected_seed_ac,
    ) = calculate_actual_canopy_cover(
        time_canopy_cover_adjusted,
        crop_time_to_emergence,
        crop_time_to_maturity,
        crop_time_to_canopy_end_development,
        crop_time_to_senescense,
        initial_canopy_cover,
        initial_canopy_cover_emergence_CC0_adj,
        canopy_cover_emergence_CC0,
        maximun_canopy_cover_CCx,
        initial_protected_seed,
        canopy_growth_coefficient_CGC,
        canopy_decline_coefficient_CDC,
        time_delta_of_canopy_growth,
        water_stress_coef.exp,
        initial_CCxAct,
        initial_is_crop_dead,
    )
    
    if canopy_cover_ac != None:
        canopy_cover = canopy_cover_ac
    if cc0_adj_ac != None:
        cc0_adj = cc0_adj_ac
    if ccx_act_ac != None:
        ccx_act = ccx_act_ac
    if is_crop_dead_ac != None:
        is_crop_dead = is_crop_dead_ac
    if protected_seed_ac != None:
        protected_seed = protected_seed_ac

    if (time_canopy_cover_adjusted >= crop_time_to_emergence) and (
        (time_canopy_cover_adjusted < crop_time_to_senescense)
        or (initial_t_early_sen > 0)
    ):
        (
            premat_senes_sws,
            t_early_sen_sws,
            canopy_cover_sws,
            ccx_act_sws,
            cc0_adj_sws,
            is_crop_dead_sws,
            ccx_w_sws,
        ) = calculate_actual_canopy_senescence_due_to_water_stress(
            water_stress_coef.sen,
            initial_protected_seed,
            initial_canopy_cover,
            initial_t_early_sen,
            time_delta_of_canopy_growth,
            crop,
            root_zone_depletion,
            taw,
            et0,
            initial_ccx_early_sen,
            time_canopy_cover_adjusted,
            crop_time_to_senescense,
            maximun_canopy_cover_CCx,
            canopy_cover_emergence_CC0,
            canopy_decline_coefficient_CDC,
            initial_is_crop_dead,
            initial_canopy_cover_emergence_CC0_adj,
            initial_CCxW,
        )
        
        if premat_senes_sws != None:
            premat_senes = premat_senes_sws

        if t_early_sen_sws != None:
            t_early_sen = t_early_sen_sws
        
        if canopy_cover_sws != None:
            canopy_cover = canopy_cover_sws

        if ccx_act_sws != None:
            ccx_act = ccx_act_sws
        
        if cc0_adj_sws != None:
            cc0_adj = cc0_adj_sws
        
        if is_crop_dead_sws != None:
            is_crop_dead = is_crop_dead_sws
        
        if ccx_w_sws != None:
            ccx_w = ccx_w_sws

    ## Calculate canopy size adjusted for micro-advective effects ##
    # Check to ensure potential canopy_cover is not slightly lower than actual
    (
        canopy_cover_ns,
        ccx_act_ns,
    ) = calculate_canopy_cover_adjusted_for_micro_advective_effects(
        canopy_cover_ns,
        canopy_cover,
        crop_time_to_canopy_end_development,
        time_canopy_cover_adjusted,
        ccx_act_ns,
    )

    canopy_cover_adj = calculate_canopy_cover_adjusted(canopy_cover)
    canopy_cover_adj_ns = calculate_canopy_cover_adjusted(canopy_cover_ns)

    return (
        canopy_cover,
        canopy_cover_adj,
        canopy_cover_ns,
        canopy_cover_adj_ns,
        ccx_w,
        ccx_act,
        ccx_w_ns,
        ccx_act_ns,
        premat_senes,
        ccx_early_sen,
        t_early_sen,
        cc0_adj,
        is_crop_dead,
        protected_seed,
    )


def choose_between_root_zone_or_top_soil_depletions(root_zone_depletion, taw):
    # Check whether to use root zone or top soil depletions for calculating
    # water stress
    if (root_zone_depletion.Rz / taw.Rz) <= (root_zone_depletion.Zt / taw.Zt):
        # Root zone is wetter than top soil, so use root zone value
        root_zone_depletion = root_zone_depletion.Rz
        taw = taw.Rz
    else:
        # Top soil is wetter than root zone, so use top soil values
        root_zone_depletion = root_zone_depletion.Zt
        taw = taw.Zt

    return root_zone_depletion, taw


def calculate_water_stress(
    crop_p_up,
    crop_p_lo,
    crop_ETadj,
    crop_beta,
    crop_fshape_w,
    t_early_sen,
    root_zone_depletion,
    taw,
    et0,
    beta,
):
    # Determine if water stress is occurring
    water_stress_coef = Ksw()
    (
        water_stress_coef.exp,
        water_stress_coef.sto,
        water_stress_coef.sen,
        water_stress_coef.pol,
        water_stress_coef.sto_lin,
    ) = water_stress(
        crop_p_up,
        crop_p_lo,
        crop_ETadj,
        crop_beta,
        crop_fshape_w,
        t_early_sen,
        root_zone_depletion,
        taw,
        et0,
        beta,
    )
    return water_stress_coef


def get_canopy_cover_growth_time(
    calendar_type, dap, delayed_cds, gdd, gdd_cum, delayed_gdds
):
    # Get canopy cover growth time
    if calendar_type == 1:
        time_delta_of_canopy_growth = 1
        time_canopy_cover_adjusted = dap - delayed_cds
    elif calendar_type == 2:
        time_delta_of_canopy_growth = gdd
        time_canopy_cover_adjusted = gdd_cum - delayed_gdds

    return time_delta_of_canopy_growth, time_canopy_cover_adjusted


def can_be_canopy_cover_development(
    time_canopy_cover_adjusted, crop_time_to_emergence, crop_time_to_maturity
):
    if (time_canopy_cover_adjusted > crop_time_to_emergence) or (
        time_canopy_cover_adjusted < crop_time_to_maturity
    ):
        return True
    else:
        # No canopy development before emergence/germination or after maturity
        return False


def can_be_canopy_growth(
    time_canopy_cover_adjusted, crop_time_to_canopy_end_development
):
    if time_canopy_cover_adjusted < crop_time_to_canopy_end_development:
        return True
    else:
        return False


def slow_canopy_development(initial_cc_ns, canopy_cover_emergence_CC0):
    if initial_cc_ns <= canopy_cover_emergence_CC0:
        return True
    else:
        return False


def calculate_slow_canopy_development(
    canopy_cover_emergence_CC0,
    canopy_growth_coefficient_CGC,
    time_delta_of_canopy_growth,
):
    # Very small initial canopy_cover.
    canopy_cover = canopy_cover_emergence_CC0 * np.exp(
        canopy_growth_coefficient_CGC * time_delta_of_canopy_growth
    )
    return canopy_cover


def is_in_mid_season_stage(time_canopy_cover_adjusted, crop_time_to_senescense):
    if time_canopy_cover_adjusted < crop_time_to_senescense:
        return True
    else:
        return False


def calculate_potential_canopy_cover(
    time_canopy_cover_adjusted,
    crop_time_to_emergence,
    crop_time_to_maturity,
    crop_time_to_canopy_end_development,
    crop_time_to_senescense,
    initial_cc_ns,
    canopy_cover_emergence_CC0,
    maximun_canopy_cover_CCx,
    canopy_growth_coefficient_CGC,
    canopy_decline_coefficient_CDC,
    time_delta_of_canopy_growth,
    initial_ccx_act_ns,
):
    # Variables to be calculated
    canopy_cover_ns = None
    cc0_adj = None
    ccx_w_ns = None
    ccx_act_ns = None

    if not can_be_canopy_cover_development(
        time_canopy_cover_adjusted, crop_time_to_emergence, crop_time_to_maturity
    ):
        canopy_cover_ns = 0
        cc0_adj = 0

    elif can_be_canopy_growth(
        time_canopy_cover_adjusted, crop_time_to_canopy_end_development
    ):
        if slow_canopy_development(initial_cc_ns, canopy_cover_emergence_CC0):
            canopy_cover_ns = calculate_slow_canopy_development(
                canopy_cover_emergence_CC0,
                canopy_growth_coefficient_CGC,
                time_delta_of_canopy_growth,
            )
        else:
            canopy_cover_growth_time_tCC = (
                time_canopy_cover_adjusted - crop_time_to_emergence
            )
            stage_canopy_cover_development = (
                "Growth"  # stage of Canopy developement (Growth or Decline)
            )
            canopy_cover_ns = cc_development(
                CCo=canopy_cover_emergence_CC0,
                CCx=0.98 * maximun_canopy_cover_CCx,
                CGC=canopy_growth_coefficient_CGC,
                CDC=canopy_decline_coefficient_CDC,
                dt=canopy_cover_growth_time_tCC,
                Mode=stage_canopy_cover_development,
                CCx0=maximun_canopy_cover_CCx,
            )
        # Update maximum canopy cover size in growing season
        ccx_act_ns = canopy_cover_ns
    else:
        # No more canopy growth is possible or canopy in decline
        # Set CCx for calculation of withered canopy effects
        ccx_w_ns = initial_ccx_act_ns
        if is_in_mid_season_stage(time_canopy_cover_adjusted, crop_time_to_senescense):
            # Mid-season stage - no canopy growth
            canopy_cover_ns = initial_cc_ns
            # Update maximum canopy cover size in growing season
            ccx_act_ns = canopy_cover_ns
        else:
            # Late-season stage - canopy decline
            canopy_cover_growth_time_tCC = (
                time_canopy_cover_adjusted - crop_time_to_senescense
            )
            stage_canopy_cover_development = (
                "Decline"  # stage of Canopy developement (Growth or Decline)
            )

            canopy_cover_ns = cc_development(
                CCo=canopy_cover_emergence_CC0,
                CCx=initial_ccx_act_ns,
                CGC=canopy_growth_coefficient_CGC,
                CDC=canopy_decline_coefficient_CDC,
                dt=canopy_cover_growth_time_tCC,
                Mode=stage_canopy_cover_development,
                CCx0=initial_ccx_act_ns,
            )

    return (canopy_cover_ns, cc0_adj, ccx_w_ns, ccx_act_ns)


def slow_actual_canopy_development(
    initial_canopy_cover, initial_canopy_cover_emergence_CC0_adj, initial_protected_seed
):
    if initial_canopy_cover <= initial_canopy_cover_emergence_CC0_adj or (
        (initial_protected_seed == True)
        and (initial_canopy_cover <= (1.25 * initial_canopy_cover_emergence_CC0_adj))
    ):
        return True
    else:
        return False


def calculate_slow_canopy_development_with_protected_seed(
    time_canopy_cover_adjusted,
    crop_time_to_emergence,
    canopy_cover_emergence_CC0,
    maximun_canopy_cover_CCx,
    canopy_growth_coefficient_CGC,
    canopy_decline_coefficient_CDC,
    initial_canopy_cover_emergence_CC0_adj,
):
    time_canopy_cover_growing = time_canopy_cover_adjusted - crop_time_to_emergence
    canopy_cover = cc_development(
        canopy_cover_emergence_CC0,
        maximun_canopy_cover_CCx,
        canopy_growth_coefficient_CGC,
        canopy_decline_coefficient_CDC,
        time_canopy_cover_growing,
        "Growth",
    )
    # Check if seed protection should be turned off
    if canopy_cover > (1.25 * initial_canopy_cover_emergence_CC0_adj):
        # Turn off seed protection - lead expansion stress can
        # occur on future time steps.
        protected_seed = False
    else:
        protected_seed = True

    return canopy_cover, protected_seed


def is_canopy_approaching_maximun_size(initial_canopy_cover, maximun_canopy_cover_CCx):
    if initial_canopy_cover >= (0.9799 * maximun_canopy_cover_CCx):
        return True
    else:
        return False


def calculate_normal_canopy_growth_with_water_stress_effects(
    canopy_growth_coefficient_CGC,
    water_stress_coef_exp,
    initial_canopy_cover,
    canopy_cover_emergence_CC0,
    initial_canopy_cover_emergence_CC0_adj,
    maximun_canopy_cover_CCx,
    canopy_decline_coefficient_CDC,
    time_delta_of_canopy_growth,
    time_canopy_cover_adjusted,
    crop_time_to_emergence,
    crop_time_to_canopy_end_development,
):
    # Variables to be returned
    canopy_cover = None
    cc0_adj = None

    # Adjust canopy growth coefficient for leaf expansion water
    # stress effects
    canopy_growth_coefficient_CGC_adj = (
        canopy_growth_coefficient_CGC * water_stress_coef_exp
    )

    if canopy_growth_coefficient_CGC_adj > 0:
        # Adjust CCx for change in CGC
        maximun_canopy_cover_CCx_adj = adjust_CCx(
            initial_canopy_cover,
            initial_canopy_cover_emergence_CC0_adj,
            maximun_canopy_cover_CCx,
            canopy_growth_coefficient_CGC_adj,
            canopy_decline_coefficient_CDC,
            time_delta_of_canopy_growth,
            time_canopy_cover_adjusted,
            crop_time_to_canopy_end_development,
            maximun_canopy_cover_CCx,
        )
        if maximun_canopy_cover_CCx_adj < 0:
            canopy_cover = initial_canopy_cover
        elif abs(initial_canopy_cover - (0.9799 * maximun_canopy_cover_CCx)) < 0.001:
            # Approaching maximum canopy cover size
            canopy_cover_growth_time_tCC = (
                time_canopy_cover_adjusted - crop_time_to_emergence
            )
            stage_canopy_cover_development = (
                "Growth"  # stage of Canopy developement (Growth or Decline)
            )

            canopy_cover = cc_development(
                canopy_cover_emergence_CC0,
                maximun_canopy_cover_CCx,
                canopy_growth_coefficient_CGC,
                canopy_decline_coefficient_CDC,
                canopy_cover_growth_time_tCC,
                stage_canopy_cover_development,
                maximun_canopy_cover_CCx,
            )
        else:
            # Determine time required to reach canopy_cover on previous,
            # day, given CGCAdj value

            time_mode = "CGC"
            time_required_reach_canopy_cover = cc_required_time(
                initial_canopy_cover,
                initial_canopy_cover_emergence_CC0_adj,
                maximun_canopy_cover_CCx_adj,
                canopy_growth_coefficient_CGC_adj,
                canopy_decline_coefficient_CDC,
                time_mode,
            )
            if time_required_reach_canopy_cover > 0:
                # Calclate gdd's for canopy growth
                canopy_cover_growth_time_tCC = (
                    time_required_reach_canopy_cover + time_delta_of_canopy_growth
                )
                stage_canopy_cover_development = (
                    "Growth"  # stage of Canopy developement (Growth or Decline)
                )

                # Determine new canopy size
                canopy_cover = cc_development(
                    initial_canopy_cover_emergence_CC0_adj,
                    maximun_canopy_cover_CCx_adj,
                    canopy_growth_coefficient_CGC_adj,
                    canopy_decline_coefficient_CDC,
                    canopy_cover_growth_time_tCC,
                    stage_canopy_cover_development,
                )

            else:
                # No canopy growth
                canopy_cover = initial_canopy_cover

    else:
        # No canopy growth
        canopy_cover = initial_canopy_cover

        # Update CC0
        if canopy_cover > initial_canopy_cover_emergence_CC0_adj:
            cc0_adj = canopy_cover_emergence_CC0
        else:
            cc0_adj = canopy_cover

    return canopy_cover, cc0_adj


def calculate_actual_canopy_cover(
    time_canopy_cover_adjusted,
    crop_time_to_emergence,
    crop_time_to_maturity,
    crop_time_to_canopy_end_development,
    crop_time_to_senescense,
    initial_canopy_cover,
    initial_canopy_cover_emergence_CC0_adj,
    canopy_cover_emergence_CC0,
    maximun_canopy_cover_CCx,
    initial_protected_seed,
    canopy_growth_coefficient_CGC,
    canopy_decline_coefficient_CDC,
    time_delta_of_canopy_growth,
    water_stress_coef_exp,
    initial_CCxAct,
    initial_is_crop_dead,
):
    # Variables to be returned
    canopy_cover = None
    cc0_adj = None
    ccx_act = None
    is_crop_dead = None
    protected_seed = None

    if not can_be_canopy_cover_development(
        time_canopy_cover_adjusted, crop_time_to_emergence, crop_time_to_maturity
    ):
        canopy_cover = 0
        cc0_adj = 0

    elif can_be_canopy_growth(
        time_canopy_cover_adjusted, crop_time_to_canopy_end_development
    ):
        if slow_actual_canopy_development(
            initial_canopy_cover,
            initial_canopy_cover_emergence_CC0_adj,
            initial_protected_seed,
        ):
            # Very small initial canopy_cover or seedling in protected phase of
            # growth. In this case, assume no leaf water expansion stress
            if initial_protected_seed == True:
                (
                    canopy_cover,
                    protected_seed,
                ) = calculate_slow_canopy_development_with_protected_seed(
                    time_canopy_cover_adjusted,
                    crop_time_to_emergence,
                    canopy_cover_emergence_CC0,
                    maximun_canopy_cover_CCx,
                    canopy_growth_coefficient_CGC,
                    canopy_decline_coefficient_CDC,
                    initial_canopy_cover_emergence_CC0_adj,
                )
            else:
                canopy_cover = initial_canopy_cover_emergence_CC0_adj * np.exp(
                    canopy_growth_coefficient_CGC * time_delta_of_canopy_growth
                )

        else:
            if not is_canopy_approaching_maximun_size(
                initial_canopy_cover, maximun_canopy_cover_CCx
            ):
                (
                    canopy_cover,
                    cc0_adj,
                ) = calculate_normal_canopy_growth_with_water_stress_effects(
                    canopy_growth_coefficient_CGC,
                    water_stress_coef_exp,
                    initial_canopy_cover,
                    canopy_cover_emergence_CC0,
                    initial_canopy_cover_emergence_CC0_adj,
                    maximun_canopy_cover_CCx,
                    canopy_decline_coefficient_CDC,
                    time_delta_of_canopy_growth,
                    time_canopy_cover_adjusted,
                    crop_time_to_emergence,
                    crop_time_to_canopy_end_development,
                )
            else:
                # Canopy approaching maximum size
                canopy_cover_growth_time_tCC = (
                    time_canopy_cover_adjusted - crop_time_to_emergence
                )
                stage_canopy_cover_development = (
                    "Growth"  # stage of Canopy developement (Growth or Decline)
                )
                canopy_cover = cc_development(
                    canopy_cover_emergence_CC0,
                    maximun_canopy_cover_CCx,
                    canopy_growth_coefficient_CGC,
                    canopy_decline_coefficient_CDC,
                    canopy_cover_growth_time_tCC,
                    stage_canopy_cover_development,
                )

                cc0_adj = canopy_cover_emergence_CC0

        if canopy_cover > initial_CCxAct:
            # Update actual maximum canopy cover size during growing season
            ccx_act = canopy_cover

        # return canopy_cover, cc0_adj, ccx_act

    else:
        # No more canopy growth is possible or canopy is in decline
        if is_in_mid_season_stage(time_canopy_cover_adjusted, crop_time_to_senescense):
            # Mid-season stage - no canopy growth
            canopy_cover = initial_canopy_cover

            if canopy_cover > initial_CCxAct:
                # Update actual maximum canopy cover size during growing season
                ccx_act = canopy_cover

        else:
            # Late-season stage - canopy decline
            # Adjust canopy decline coefficient for difference between actual
            # and potential CCx
            canopy_decline_coefficient_CDC_adj = canopy_decline_coefficient_CDC * (
                (initial_CCxAct + 2.29) / (maximun_canopy_cover_CCx + 2.29)
            )
            # Determine new canopy size
            canopy_cover_growth_time_tCC = (
                time_canopy_cover_adjusted - crop_time_to_senescense
            )

            stage_canopy_cover_development = "Decline"

            canopy_cover = cc_development(
                initial_canopy_cover_emergence_CC0_adj,
                initial_CCxAct,
                canopy_growth_coefficient_CGC,
                canopy_decline_coefficient_CDC_adj,
                canopy_cover_growth_time_tCC,
                stage_canopy_cover_development,
                initial_CCxAct,
            )

        # Check for crop growth termination
        if (canopy_cover < 0.001) and (initial_is_crop_dead == False):
            # crop has died
            canopy_cover = 0
            is_crop_dead = True

    return canopy_cover, cc0_adj, ccx_act, is_crop_dead, protected_seed


def calculate_actual_canopy_senescence_due_to_water_stress(
    water_stress_coef_sen,
    initial_protected_seed,
    initial_canopy_cover,
    initial_t_early_sen,
    time_delta_of_canopy_growth,
    crop,
    root_zone_depletion,
    taw,
    et0,
    initial_ccx_early_sen,
    time_canopy_cover_adjusted,
    crop_time_to_senescense,
    maximun_canopy_cover_CCx,
    canopy_cover_emergence_CC0,
    canopy_decline_coefficient_CDC,
    initial_is_crop_dead,
    initial_canopy_cover_emergence_CC0_adj,
    initial_CCxW,
):
    # Variables to be returned
    canopy_cover = None
    is_crop_dead = None
    ccx_act = None
    cc0_adj = None
    ccx_w = None
    t_early_sen = None
    premat_senes = None

    if (water_stress_coef_sen < 1) and (initial_protected_seed == False):
        # early canopy senescence due to severe water stress
        premature_senescence = True

        if initial_t_early_sen == 0:
            # No prior early senescence
            initial_ccx_early_sen = initial_canopy_cover

        # Increment early senescence gdd counter
        t_early_sen = initial_t_early_sen + time_delta_of_canopy_growth

        # Adjust canopy decline coefficient for water stress
        beta = False

        water_stress_coef = calculate_water_stress(
            crop_p_up=crop.P_up,
            crop_p_lo=crop.P_lo,
            crop_ETadj=crop.ETadj,
            crop_beta=crop.beta,
            crop_fshape_w=crop.fshape_w,
            t_early_sen=t_early_sen,
            root_zone_depletion=root_zone_depletion,
            taw=taw,
            et0=et0,
            beta=False,
        )

        # water_stress_coef = water_stress(crop, NewCond, root_zone_depletion, taw, et0, beta)
        if water_stress_coef.sen > 0.99999:
            canopy_decline_coefficient_CDC_adj = 0.0001
        else:
            canopy_decline_coefficient_CDC_adj = (
                1 - (water_stress_coef.sen**8)
            ) * canopy_decline_coefficient_CDC

        # Get new canpy cover size after senescence
        if initial_ccx_early_sen < 0.001:
            # No prior early senescence
            canopy_cover_sen = 0
        else:
            # Get time required to reach canopy_cover at end of previous day, given
            # CDCadj
            time_required_reach_canopy_cover = (
                np.log(1 + (1 - initial_canopy_cover / initial_ccx_early_sen) / 0.05)
            ) / (
                (canopy_decline_coefficient_CDC_adj * 3.33)
                / (initial_ccx_early_sen + 2.29)
            )

            # Calculate gdd's for canopy decline
            # TODO: It the variable name correct?
            canopy_cover_growth_time_tCC = (
                time_required_reach_canopy_cover + time_delta_of_canopy_growth
            )
            # Determine new canopy size
            canopy_cover_sen = initial_ccx_early_sen * (
                1
                - 0.05
                * (
                    np.exp(
                        canopy_cover_growth_time_tCC
                        * (
                            (canopy_decline_coefficient_CDC_adj * 3.33)
                            / (initial_ccx_early_sen + 2.29)
                        )
                    )
                    - 1
                )
            )
            if canopy_cover_sen < 0:
                canopy_cover_sen = 0

        # Update canopy cover size
        if time_canopy_cover_adjusted < crop_time_to_senescense:
            # Limit canopy_cover to CCx
            if canopy_cover_sen > maximun_canopy_cover_CCx:
                canopy_cover_sen = maximun_canopy_cover_CCx

            # canopy_cover cannot be greater than value on previous day
            canopy_cover = canopy_cover_sen

            if canopy_cover > initial_canopy_cover:
                canopy_cover = initial_canopy_cover

            # Update maximum canopy cover size during growing
            # season
            ccx_act = canopy_cover

            # Update CC0 if current canopy_cover is less than initial canopy
            # cover size at planting
            if canopy_cover < canopy_cover_emergence_CC0:
                cc0_adj = canopy_cover
            else:
                cc0_adj = canopy_cover_emergence_CC0

        else:
            # Update canopy_cover to account for canopy cover senescence due
            # to water stress
            if canopy_cover_sen < initial_canopy_cover:
                canopy_cover = canopy_cover_sen

        # Check for crop growth termination
        if (canopy_cover < 0.001) and (initial_is_crop_dead == False):
            # crop has died
            canopy_cover = 0
            is_crop_dead = True
    else:
        # No water stress
        premat_senes = False
        if (time_canopy_cover_adjusted > crop_time_to_senescense) and (
            initial_t_early_sen > 0
        ):
            # Rewatering of canopy in late season
            # Get new values for CCx and CDC
            tmp_tCC = (
                time_canopy_cover_adjusted
                - time_delta_of_canopy_growth
                - crop_time_to_senescense
            )
            (
                maximun_canopy_cover_CCx_adj,
                canopy_decline_coefficient_CDC_adj,
            ) = update_CCx_CDC(initial_canopy_cover, crop.CDC, crop.CCx, tmp_tCC)
            ccx_act = maximun_canopy_cover_CCx
            # Get new canopy_cover value for end of current day
            tmp_tCC = time_canopy_cover_adjusted - crop.Senescence
            canopy_cover = cc_development(
                initial_canopy_cover_emergence_CC0_adj,
                maximun_canopy_cover_CCx_adj,
                crop.CGC,
                canopy_decline_coefficient_CDC_adj,
                tmp_tCC,
                "Decline",
                maximun_canopy_cover_CCx_adj,
            )

            # Check for crop growth termination
            if (canopy_cover < 0.001) and (initial_is_crop_dead == False):
                canopy_cover = 0
                is_crop_dead = True

        # Reset early senescence counter
        t_early_sen = 0

    # Adjust CCx for effects of withered canopy
    if initial_canopy_cover > initial_CCxW:
        ccx_w = canopy_cover

    return (
        premat_senes,
        t_early_sen,
        canopy_cover,
        ccx_act,
        cc0_adj,
        is_crop_dead,
        ccx_w,
    )


def calculate_canopy_cover_adjusted_for_micro_advective_effects(
    canopy_cover_ns,
    canopy_cover,
    crop_time_to_canopy_end_development,
    time_canopy_cover_adjusted,
    ccx_act_ns,
):
    if canopy_cover_ns < canopy_cover:
        canopy_cover_ns = canopy_cover
        if time_canopy_cover_adjusted < crop_time_to_canopy_end_development:
            ccx_act_ns = canopy_cover_ns

    return canopy_cover_ns, ccx_act_ns


def calculate_canopy_cover_adjusted(canopy_cover):
    canopy_cover_adj = (
        (1.72 * canopy_cover) - (canopy_cover**2) + (0.3 * (canopy_cover**3))
    )
    return canopy_cover_adj
