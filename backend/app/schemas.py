from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

NonNegative = Annotated[float, Field(ge=0,le=1e9,allow_inf_nan=False)]
Rate = Annotated[float, Field(ge=0,le=1,allow_inf_nan=False)]
Product = Literal['traje','efeito','colecao','passe','sazonal']


class Overrides(BaseModel):
    model_config = ConfigDict(extra='forbid',allow_inf_nan=False)
    cac: NonNegative | None = None
    acq: Annotated[int,Field(ge=1,le=1000000)] | None = None
    eng: Annotated[float,Field(ge=0,le=100)] | None = None
    spend: Annotated[float,Field(ge=0,le=10)] | None = None
    opex: Annotated[float,Field(ge=0,le=10)] | None = None
    elasticity: Annotated[float,Field(ge=0,le=5)] | None = None
    price_mult: dict[Product,Annotated[float,Field(ge=.05,le=10)]] | None = None
    activity: list[Rate] | None = Field(default=None,min_length=12,max_length=12)
    capital: NonNegative | None = None
    reserve: NonNegative | None = None
    fee: Rate | None = None
    tax: Rate | None = None
    refund: Rate | None = None
    operations: NonNegative | None = None
    production: NonNegative | None = None
    content: NonNegative | None = None
    unit_cost: dict[Product,NonNegative] | None = None
    attractiveness: dict[Product,Rate] | None = None


class SimulationInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    strategy: Literal['A','B','C'] = 'A'
    scenario: Literal['central','conservador','otimista','estresse'] = 'central'
    name: str = Field(default='Minha simulação',min_length=1,max_length=100)
    overrides: Overrides = Field(default_factory=Overrides)

    @model_validator(mode='after')
    def valid_parameters(self):
        from .simulation.engine import parameters, CAT
        o = self.overrides.model_dump(exclude_none=True)
        for key in ('price_mult','unit_cost','attractiveness'):
            if key in o and set(o[key]) != set(CAT):
                raise ValueError(f'{key} deve conter os cinco produtos')
        p = parameters(self.strategy,self.scenario,o)
        if p['fee']+p['tax']>1: raise ValueError('Tarifas e tributos excedem 100%')
        if sum(p['attractiveness'].values())>=1: raise ValueError('Atratividade total deve ser menor que 100%')
        if p['reserve']>p['capital']: raise ValueError('Reserva não pode exceder capital')
        if not self.name.strip(): raise ValueError('Nome obrigatório')
        return self


class MonthlyResult(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    strategy: Literal['A','B','C']
    scenario: Literal['central','conservador','otimista','estresse']
    month: int
    new: float
    active: float
    p_buy: float
    buyers: float
    units_traje: float
    units_efeito: float
    units_colecao: float
    units_passe: float
    units_sazonal: float
    gross: float
    refunds: float
    platform: float
    tax: float
    net: float
    variable: float
    production: float
    content: float
    operations: float
    marketing: float
    costs: float
    flow: float
    cash: float
    usable_cash: float
    cumulative_flow: float


class SummaryResult(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    gross: float
    refunds: float
    platform: float
    tax: float
    net: float
    variable: float
    production: float
    content: float
    operations: float
    marketing: float
    costs: float
    flow: float
    active_player_months: float
    acquired: float
    buyers_months: float
    cac: float
    contribution: float
    recoverable_contribution: float
    ltv_partial: float
    arpu: float
    arppu: float | None
    cash: float
    reserve: float
    insufficient_month: int | None
    cash_negative_month: int | None
    max_cac_after_fixed: float
    break_even_acquired: float | None
    break_even_active_months: float | None


class CohortResult(BaseModel):
    cohort_month: int
    horizon_months: int
    acquired: float
    active_player_months: float
    gross: float
    contribution_before_CAC: float
    contribution_per_acquired: float
    CAC: float
    net_after_CAC: float


class ProductResult(BaseModel):
    id: Product
    name: str
    price: float
    probability: float
    units: float
    gross: float


class SimulationResult(BaseModel):
    model_version: str
    model_hash: str
    strategy: str
    scenario: str
    parameters: dict
    summary: SummaryResult
    months: list[MonthlyResult]
    cohorts: list[CohortResult]
    products: list[ProductResult]
    none_probability: float
