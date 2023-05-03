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
    initial_cc = initialCond.canopy_cover  # initial canopy cover
    initial_protected_seed = initialCond.protected_seed
    initial_CCxAct = initialCond.ccx_act
    initial_is_crop_dead = initialCond.crop_dead  # Is crop dead? (True, False)
    initial_tEarlySen = initialCond.t_early_sen
    initial_CCxW = initialCond.ccx_w

    # Values needed
    z_root = float(initialCond.z_root)  # rooting depth [mm]
    th = initialCond.th  # Water content in the root zone (TODO: CHECK this)
    z_min = float(initialCond.z_min)  # minimum depth of the root zone [mm]
    aeration_stress = (
        crop.Aer
    )  # Vol (%) below saturation at which stress begins to occur due to deficient aeration
    dap = initialCond.dap  # days after planting
    delayed_cds = crop.DelayedCDs  # delayed crop development stage (days) TODO: CHECK this
    gdd_cum = initialCond.gdd_cum  # cumulative growing degree days
    delayed_gdds = crop.DelayedGDDs  # delayed growing degree days (days) TODO: Check this
    
    

    ## Store initial conditions in a new structure for updating ##
    NewCond = initialCond
    NewCond.cc_prev = initialCond.canopy_cover

    ## Calculate canopy development (if in growing season) ##
    if growing_season == True:
        canopy_cover_in_growing_season(
            soil_profile=soil_profile,
            z_root=z_root,
            th=th,
            top_soil_depth_zTop=top_soil_depth_zTop,
            aeration_stress=aeration_stress,
            crop=crop,
            gdd=gdd,
            et0=et0,
            initial_dap=dap,
        initial_delayed_cds=delayed_cds,
        initial_gdd_cum=gdd_cum,
        initial_delayed_gdds=delayed_gdds,
            )

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
    initial_t_early_sen,
    root_zone_depletion,
    taw,
    et0,
    beta,
):
    # Determine if water stress is occurring
    beta = True
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
        initial_t_early_sen,
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
        dtCC = 1
        tCCadj = dap - delayed_cds
    elif calendar_type == 2:
        dtCC = gdd
        tCCadj = gdd_cum - delayed_gdds

    return dtCC, tCCadj


def canopy_cover_in_growing_season(
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
    initial_gdd_cum,
    initial_delayed_gdds,
):
    # Calculate root zone water content
    taw = TAW()
    root_zone_depletion = Dr()

    # thRZ = RootZoneWater()
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

    # _,root_zone_depletion,taw,_ = root_zone_water(Soil_Profile,float(NewCond.z_root),NewCond.th,top_soil_depth_zTop,float(crop.Zmin),crop.Aer)
    root_zone_depletion, taw = choose_between_root_zone_or_top_soil_depletions(
        root_zone_depletion=root_zone_depletion, taw=taw
    )

    water_stress_coef = calculate_water_stress(
        crop_p_up=crop.P_up,
        crop_p_lo=crop.P_lo,
        crop_ETadj=crop.ETadj,
        crop_beta=crop.beta,
        crop_fshape_w=crop.fshape_w,
        initial_t_early_sen=crop.t_early_sen,
        root_zone_depletion=root_zone_depletion,
        taw=taw,
        et0=et0,
        beta=beta,
    )

    calendar_type = crop.CalendarType
    dap = initial_dap
    delayed_cds = initial_delayed_cds
    gdd = gdd
    gdd_cum = initial_gdd_cum
    delayed_gdds = initial_delayed_gdds

    dtCC, tCCadj = get_canopy_cover_growth_time(
        calendar_type=calendar_type,
        dap=dap,
        delayed_cds=delayed_cds,
        gdd=gdd,
        gdd_cum=gdd_cum,
        delayed_gdds=delayed_gdds,
    )

    ## Canopy development (potential) ##
    if (tCCadj < crop.Emergence) or (round(tCCadj) > crop.Maturity):
        # No canopy development before emergence/germination or after
        # maturity
        NewCond.canopy_cover_ns = 0
    elif tCCadj < crop.CanopyDevEnd:
        # Canopy growth can occur
        if initial_cc_ns <= crop.CC0:
            # Very small initial canopy_cover.
            NewCond.canopy_cover_ns = crop.CC0 * np.exp(crop.CGC * dtCC)
            # print(crop.CC0,np.exp(crop.CGC*dtCC))
        else:
            # Canopy growing
            tmp_tCC = tCCadj - crop.Emergence
            NewCond.canopy_cover_ns = cc_development(
                crop.CC0,
                0.98 * crop.CCx,
                crop.CGC,
                crop.CDC,
                tmp_tCC,
                "Growth",
                crop.CCx,
            )

        # Update maximum canopy cover size in growing season
        NewCond.ccx_act_ns = NewCond.canopy_cover_ns
    elif tCCadj > crop.CanopyDevEnd:
        # No more canopy growth is possible or canopy in decline
        # Set CCx for calculation of withered canopy effects
        NewCond.ccx_w_ns = NewCond.ccx_act_ns
        if tCCadj < crop.Senescence:
            # Mid-season stage - no canopy growth
            NewCond.canopy_cover_ns = initial_cc_ns
            # Update maximum canopy cover size in growing season
            NewCond.ccx_act_ns = NewCond.canopy_cover_ns
        else:
            # Late-season stage - canopy decline
            tmp_tCC = tCCadj - crop.Senescence
            NewCond.canopy_cover_ns = cc_development(
                crop.CC0,
                NewCond.ccx_act_ns,
                crop.CGC,
                crop.CDC,
                tmp_tCC,
                "Decline",
                NewCond.ccx_act_ns,
            )

    ## Canopy development (actual) ##
    if (tCCadj < crop.Emergence) or (round(tCCadj) > crop.Maturity):
        # No canopy development before emergence/germination or after
        # maturity
        NewCond.canopy_cover = 0
        NewCond.cc0_adj = crop.CC0
    elif tCCadj < crop.CanopyDevEnd:
        # Canopy growth can occur
        if initial_cc <= NewCond.cc0_adj or (
            (initial_protected_seed == True)
            and (initial_cc <= (1.25 * NewCond.cc0_adj))
        ):
            # Very small initial canopy_cover or seedling in protected phase of
            # growth. In this case, assume no leaf water expansion stress
            if initial_protected_seed == True:
                tmp_tCC = tCCadj - crop.Emergence
                NewCond.canopy_cover = cc_development(
                    crop.CC0, crop.CCx, crop.CGC, crop.CDC, tmp_tCC, "Growth", crop.CCx
                )
                # Check if seed protection should be turned off
                if NewCond.canopy_cover > (1.25 * NewCond.cc0_adj):
                    # Turn off seed protection - lead expansion stress can
                    # occur on future time steps.
                    NewCond.protected_seed = False

            else:
                NewCond.canopy_cover = NewCond.cc0_adj * np.exp(crop.CGC * dtCC)

        else:
            # Canopy growing

            if initial_cc < (0.9799 * crop.CCx):
                # Adjust canopy growth coefficient for leaf expansion water
                # stress effects
                CGCadj = crop.CGC * water_stress_coef.exp
                if CGCadj > 0:
                    # Adjust CCx for change in CGC
                    CCXadj = adjust_CCx(
                        initial_cc,
                        NewCond.cc0_adj,
                        crop.CCx,
                        CGCadj,
                        crop.CDC,
                        dtCC,
                        tCCadj,
                        crop.CanopyDevEnd,
                        crop.CCx,
                    )
                    if CCXadj < 0:
                        NewCond.canopy_cover = initial_cc
                    elif abs(initial_cc - (0.9799 * crop.CCx)) < 0.001:
                        # Approaching maximum canopy cover size
                        tmp_tCC = tCCadj - crop.Emergence
                        NewCond.canopy_cover = cc_development(
                            crop.CC0,
                            crop.CCx,
                            crop.CGC,
                            crop.CDC,
                            tmp_tCC,
                            "Growth",
                            crop.CCx,
                        )
                    else:
                        # Determine time required to reach canopy_cover on previous,
                        # day, given CGCAdj value
                        tReq = cc_required_time(
                            initial_cc, NewCond.cc0_adj, CCXadj, CGCadj, crop.CDC, "CGC"
                        )
                        if tReq > 0:
                            # Calclate gdd's for canopy growth
                            tmp_tCC = tReq + dtCC
                            # Determine new canopy size
                            NewCond.canopy_cover = cc_development(
                                NewCond.cc0_adj,
                                CCXadj,
                                CGCadj,
                                crop.CDC,
                                tmp_tCC,
                                "Growth",
                                crop.CCx,
                            )
                            # print(NewCond.dap,CCXadj,tReq)

                        else:
                            # No canopy growth
                            NewCond.canopy_cover = initial_cc

                else:
                    # No canopy growth
                    NewCond.canopy_cover = initial_cc
                    # Update CC0
                    if NewCond.canopy_cover > NewCond.cc0_adj:
                        NewCond.cc0_adj = crop.CC0
                    else:
                        NewCond.cc0_adj = NewCond.canopy_cover

            else:
                # Canopy approaching maximum size
                tmp_tCC = tCCadj - crop.Emergence
                NewCond.canopy_cover = cc_development(
                    crop.CC0, crop.CCx, crop.CGC, crop.CDC, tmp_tCC, "Growth", crop.CCx
                )
                NewCond.cc0_adj = crop.CC0

        if NewCond.canopy_cover > initial_CCxAct:
            # Update actual maximum canopy cover size during growing season
            NewCond.ccx_act = NewCond.canopy_cover

    elif tCCadj > crop.CanopyDevEnd:
        # No more canopy growth is possible or canopy is in decline
        if tCCadj < crop.Senescence:
            # Mid-season stage - no canopy growth
            NewCond.canopy_cover = initial_cc
            if NewCond.canopy_cover > initial_CCxAct:
                # Update actual maximum canopy cover size during growing
                # season
                NewCond.ccx_act = NewCond.canopy_cover

        else:
            # Late-season stage - canopy decline
            # Adjust canopy decline coefficient for difference between actual
            # and potential CCx
            CDCadj = crop.CDC * ((NewCond.ccx_act + 2.29) / (crop.CCx + 2.29))
            # Determine new canopy size
            tmp_tCC = tCCadj - crop.Senescence
            NewCond.canopy_cover = cc_development(
                NewCond.cc0_adj,
                NewCond.ccx_act,
                crop.CGC,
                CDCadj,
                tmp_tCC,
                "Decline",
                NewCond.ccx_act,
            )

        # Check for crop growth termination
        if (NewCond.canopy_cover < 0.001) and (initial_is_crop_dead == False):
            # crop has died
            NewCond.canopy_cover = 0
            NewCond.crop_dead = True

    ## Canopy senescence due to water stress (actual) ##
    if tCCadj >= crop.Emergence:
        if (tCCadj < crop.Senescence) or (initial_tEarlySen > 0):
            # Check for early canopy senescence  due to severe water
            # stress.
            if (water_stress_coef.sen < 1) and (initial_protected_seed == False):
                # Early canopy senescence
                NewCond.premat_senes = True
                if initial_tEarlySen == 0:
                    # No prior early senescence
                    NewCond.ccx_early_sen = initial_cc

                # Increment early senescence gdd counter
                NewCond.t_early_sen = initial_tEarlySen + dtCC
                # Adjust canopy decline coefficient for water stress
                beta = False

                water_stress_coef = Ksw()
                (
                    water_stress_coef.exp,
                    water_stress_coef.sto,
                    water_stress_coef.sen,
                    water_stress_coef.pol,
                    water_stress_coef.sto_lin,
                ) = water_stress(
                    crop.p_up,
                    crop.p_lo,
                    crop.ETadj,
                    crop.beta,
                    crop.fshape_w,
                    NewCond.t_early_sen,
                    root_zone_depletion,
                    taw,
                    et0,
                    beta,
                )

                # water_stress_coef = water_stress(crop, NewCond, root_zone_depletion, taw, et0, beta)
                if water_stress_coef.sen > 0.99999:
                    CDCadj = 0.0001
                else:
                    CDCadj = (1 - (water_stress_coef.sen**8)) * crop.CDC

                # Get new canpy cover size after senescence
                if NewCond.ccx_early_sen < 0.001:
                    CCsen = 0
                else:
                    # Get time required to reach canopy_cover at end of previous day, given
                    # CDCadj
                    tReq = (
                        np.log(1 + (1 - initial_cc / NewCond.ccx_early_sen) / 0.05)
                    ) / ((CDCadj * 3.33) / (NewCond.ccx_early_sen + 2.29))
                    # Calculate gdd's for canopy decline
                    tmp_tCC = tReq + dtCC
                    # Determine new canopy size
                    CCsen = NewCond.ccx_early_sen * (
                        1
                        - 0.05
                        * (
                            np.exp(
                                tmp_tCC
                                * ((CDCadj * 3.33) / (NewCond.ccx_early_sen + 2.29))
                            )
                            - 1
                        )
                    )
                    if CCsen < 0:
                        CCsen = 0

                # Update canopy cover size
                if tCCadj < crop.Senescence:
                    # Limit canopy_cover to CCx
                    if CCsen > crop.CCx:
                        CCsen = crop.CCx

                    # canopy_cover cannot be greater than value on previous day
                    NewCond.canopy_cover = CCsen
                    if NewCond.canopy_cover > initial_cc:
                        NewCond.canopy_cover = initial_cc

                    # Update maximum canopy cover size during growing
                    # season
                    NewCond.ccx_act = NewCond.canopy_cover
                    # Update CC0 if current canopy_cover is less than initial canopy
                    # cover size at planting
                    if NewCond.canopy_cover < crop.CC0:
                        NewCond.cc0_adj = NewCond.canopy_cover
                    else:
                        NewCond.cc0_adj = crop.CC0

                else:
                    # Update canopy_cover to account for canopy cover senescence due
                    # to water stress
                    if CCsen < NewCond.canopy_cover:
                        NewCond.canopy_cover = CCsen

                # Check for crop growth termination
                if (NewCond.canopy_cover < 0.001) and (initial_is_crop_dead == False):
                    # crop has died
                    NewCond.canopy_cover = 0
                    NewCond.crop_dead = True

            else:
                # No water stress
                NewCond.premat_senes = False
                if (tCCadj > crop.Senescence) and (initial_tEarlySen > 0):
                    # Rewatering of canopy in late season
                    # Get new values for CCx and CDC
                    tmp_tCC = tCCadj - dtCC - crop.Senescence
                    CCXadj, CDCadj = update_CCx_CDC(
                        initial_cc, crop.CDC, crop.CCx, tmp_tCC
                    )
                    NewCond.ccx_act = CCXadj
                    # Get new canopy_cover value for end of current day
                    tmp_tCC = tCCadj - crop.Senescence
                    NewCond.canopy_cover = cc_development(
                        NewCond.cc0_adj,
                        CCXadj,
                        crop.CGC,
                        CDCadj,
                        tmp_tCC,
                        "Decline",
                        CCXadj,
                    )
                    # Check for crop growth termination
                    if (NewCond.canopy_cover < 0.001) and (
                        initial_is_crop_dead == False
                    ):
                        NewCond.canopy_cover = 0
                        NewCond.crop_dead = True

                # Reset early senescence counter
                NewCond.t_early_sen = 0

            # Adjust CCx for effects of withered canopy
            if NewCond.canopy_cover > initial_CCxW:
                NewCond.ccx_w = NewCond.canopy_cover

    ## Calculate canopy size adjusted for micro-advective effects ##
    # Check to ensure potential canopy_cover is not slightly lower than actual
    if NewCond.canopy_cover_ns < NewCond.canopy_cover:
        NewCond.canopy_cover_ns = NewCond.canopy_cover
        if tCCadj < crop.CanopyDevEnd:
            NewCond.ccx_act_ns = NewCond.canopy_cover_ns

    # Actual (with water stress)
    NewCond.canopy_cover_adj = (
        (1.72 * NewCond.canopy_cover)
        - (NewCond.canopy_cover**2)
        + (0.3 * (NewCond.canopy_cover**3))
    )
    # Potential (without water stress)
    NewCond.canopy_cover_adj_ns = (
        (1.72 * NewCond.canopy_cover_ns)
        - (NewCond.canopy_cover_ns**2)
        + (0.3 * (NewCond.canopy_cover_ns**3))
    )
