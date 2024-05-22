from pytrnsys.costCalculation.models.common import LinearCoefficients
from pytrnsys.costCalculation.models.input import Component
from pytrnsys.costCalculation.models.input import ComponentGroup
from pytrnsys.costCalculation.models.input import Input
from pytrnsys.costCalculation.models.input import Parameters
from pytrnsys.costCalculation.models.input import Variable
from pytrnsys.costCalculation.models.input import YearlyCost
from pytrnsys.utils.uncertainFloat import UncertainFloat

_BASE_COMPONENT_GROUPS = [
    ComponentGroup(
        name="TES",
        components=[
            Component(
                name="Pit Storage",
                coeffs=LinearCoefficients(
                    offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                    slope=UncertainFloat(mean=65.0, toLowerBound=0, toUpperBound=0),
                ),
                variable=Variable(name="Vol_TesUsed", unit="m$^3$"),
                lifetimeInYears=30,
            )
        ],
    ),
    ComponentGroup(
        name="Col",
        components=[
            Component(
                name="Collector",
                coeffs=LinearCoefficients(
                    offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                    slope=UncertainFloat(mean=400.0, toLowerBound=0, toUpperBound=0),
                ),
                variable=Variable(name="AcollAp", unit="m$^2$"),
                lifetimeInYears=30,
            )
        ],
    ),
    ComponentGroup(
        name="Air Source",
        components=[
            Component(
                name="Air Heat Exchanger",
                coeffs=LinearCoefficients(
                    offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                    slope=UncertainFloat(mean=100.0, toLowerBound=0, toUpperBound=0),
                ),
                variable=Variable(name="AirHxSize", unit="kW"),
                lifetimeInYears=30,
            )
        ],
    ),
]


def _createConfig(iceStorageComponentGroup: ComponentGroup) -> Input:
    return Input(
        componentGroups=[
            *_BASE_COMPONENT_GROUPS,
            iceStorageComponentGroup,
        ],
        yearlyCosts=[
            YearlyCost(
                name="Yearly cost",
                coeffs=LinearCoefficients(
                    offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                    slope=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                ),
                variable=Variable(name="E_yearly_used", unit="kWh"),
            )
        ],
        parameters=Parameters(
            rate=0.01,
            analysisPeriod=30,
            qDemandVariable=Variable(name="Q_heat_used", unit="kWh"),
            elFromGridVariable=Variable(name="E_yearly_used", unit="kWh"),
            costElecFix=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
            costElecKWh=UncertainFloat(mean=0.2, toLowerBound=0, toUpperBound=0),
            increaseElecCost=0.0,
            maintenanceRate=UncertainFloat(mean=0.01, toLowerBound=0, toUpperBound=0),
            costResidual=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
            lifetimeResVal=30,
            cleanModeLatex=True,
            reportAuthor="<not-set>",
            reportEmail="<not-set>",
        ),
    )


_SOLID_ICE_STORE_COMPONENT_GROUP = ComponentGroup(
    name="IceStorage",
    components=[
        Component(
            name="concrete casing and digging",
            coeffs=LinearCoefficients(
                offset=UncertainFloat(mean=21967.0, toLowerBound=0, toUpperBound=0),
                slope=UncertainFloat(mean=248.3, toLowerBound=0, toUpperBound=0),
            ),
            variable=Variable(name="VIceS", unit="m$^3$"),
            lifetimeInYears=20,
        ),
        Component(
            name="heat exchanger",
            coeffs=LinearCoefficients(
                offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                slope=UncertainFloat(mean=352.0, toLowerBound=0, toUpperBound=0),
            ),
            variable=Variable(name="VIceS", unit="m$^3$"),
            lifetimeInYears=20,
        ),
    ],
)

SOLID_ICE_STORE_INPUT = _createConfig(_SOLID_ICE_STORE_COMPONENT_GROUP)


_SLURRY_ICE_STORE_COMPONENT_GROUP = ComponentGroup(
    name="IceSlurryStorage",
    components=[
        Component(
            name="pit storage casing",
            coeffs=LinearCoefficients(
                offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                slope=UncertainFloat(mean=100.0, toLowerBound=0, toUpperBound=0),
            ),
            variable=Variable(name="VIceS", unit="m$^3$"),
            lifetimeInYears=20,
        ),
        Component(
            name="Crystallizer",
            coeffs=LinearCoefficients(
                offset=UncertainFloat(mean=0.0, toLowerBound=0, toUpperBound=0),
                slope=UncertainFloat(mean=100.0, toLowerBound=0, toUpperBound=0),
            ),
            variable=Variable(name="CrysPowerkW", unit="kW"),
            lifetimeInYears=20,
        ),
    ],
)


SLURRY_ICE_STORE_INPUT = _createConfig(_SLURRY_ICE_STORE_COMPONENT_GROUP)
