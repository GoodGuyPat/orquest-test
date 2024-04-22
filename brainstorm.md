 ### Notes:
- A pesar de que en el enunciado del problema se especifica que las asociaciones pueden solaparse (en el caso de que un trabajador cambie temporalmente de centro), no se da nunca el caso en la data de ejemplo. Ésto, junto con el hecho de que todos los trabajadores del ejemplo que tienen declarada al menos una asociación, la tienen siempre con la misma tienda, me lleva a concluir que la tabla associations no contiene todas las asociaciones, sino únicamente aquellas en las que un trabajador se translada a una tienda distinta a su tienda original.
- person_ids 1851178, 1851177, 665956, 1201829 y 1529075 tienen asociaciones duplicadas. ¿Entiendo que simulan input errors y las debo ignorar?
- Si la tabla asociaciones sólo contiene los casos excepcionales, no veo una manera fiable de determinar a qué tienda corresponde regularmente cada trabajador. Lo único que se me ocurre es inferirlo en base a asociaciones (al fin y al cabo, si un trabajador va excepcionalmente a tienda 2, se asume que le es regular la tienda 1). Sin embargo, éste método no me parece recomendable, dado que si un trabajador no ha tenido asociaciones excepcionales no le sería aplicable esta lógica, la cual se desmoronaría de todos modos en cuanto tengamos una tercera tienda. Entiendo que correspondería a la tabla contracts la adición de una referencia a store_id.
- Las tablas associations, contracts, hours, e incidences contienen la columna person_id. Sin embargo, los valores de person_id de la tabla contracts no tienen ninguna correspondencia con los de las otras tablas (las cuales sí las tienen entre sí). Mi sensación es que se ha perdido la última cifra de los valores de contracts, dado que los valores de las otras tablas van de 6xxxxx a 1xxxxxx (6 cifras empezando por 6 a 7 cifras empezando por 1) y los valores de contracts van de 6xxxx a 1xxxxx (5 cifras empezando por 6 a 6 cifras empezando por 1).
- 
### Inputs:
- Measures: histórico de ventas, tickets y tráfico, por cada media hora (los valores de cada hora y media son los mismos que a en punto, lo cual lleva a pensar que es simplemente el total de hora / 2)
    - measure: str (FOOTFALL, SALES, TICKETS)
    - date: datetime
    - value: int
    - store_id: int FK stores
- hours: histórico de horas de trabajo planificadas, por empleado y hora
    - day: date
    - hour: int
    - person_id:int FK persons
    - worked_hours: float
- Associations: listado de asociaciones a tienda. Cada empleado no pertenece a una tienda concreta de forma fija.
    - person_id: int FK persons
    - from_date: date
    - to_date: date
    - store_id: int FK stores
- Contracts: listado de contratos, con el coste por hora de cada empleado
    - person_id: int FK persons
    - cost_per_hour: float
    - from_date: date
    - to_date: date
- Incidences: listado de incidencias que han impedido que las personas afectadas asistieran a su puesto de trabajo durante el tiempo que duraron
    - person_id: int FK persons
    - type_name: str
    - from_date: date
    - to_date: date

### Outputs:
- Dim:
    - [x] Stores
    - [x] Persons
- Fact:
    - [x] FOOTFALL
    - [x] SALES
    - [x] TICKETS
    - [x] ASSOCIATIONS
    - [x] CONTRACTS
    - [x] INCIDENCES

- Wide tables:
    - Daily employee work log (join hours, associations, incidences)
    - 
- Analysis:
    - [ ] Employee calendar
    - [ ] Employee work log (cost per hour, running cost, running hours, running incidences, seniority)
    - [ ] Staff houry distribution
    - [ ] Distribución de cesiones por tienda
    - [ ] Log de cesiones por tienda
    - [ ] Evolución de coste de plantilla
    - [ ] Ventas por tienda y hora
    - [ ] Ventas por tienda y día
    - [ ] Store hourly evolution (traffic, sales, tickets, staff)
- Dashboards

### Diseño:
Tablas tal cual a raw.
Modelado leyendo de raw y volcando en BI.
Análisis en Metabase.

Una rama va a hacer el modelado con Pandas y otra con dbt.
