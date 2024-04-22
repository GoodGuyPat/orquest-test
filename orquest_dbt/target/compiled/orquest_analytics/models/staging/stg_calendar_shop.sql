
-- Each planned date must fall within an association which has a store assigned to it.
-- Since multiple associations may be valid at once (in which case one exists as an
-- interruption inside another), we will only use the latest active for any given day.
WITH  __dbt__cte__stg_calendar_hours as (

select day, person_id, sum(worked_hours) as worked_hours
 from "orquest_db"."orquest_raw"."hours"
 group by day, person_id order by day, person_id
), joined AS (
    SELECT
        A.*,
        b.store_id,
        ROW_NUMBER() over(
            PARTITION BY A.person_id,
            DAY
            ORDER BY
                from_date ASC
        ) AS rnum
    FROM
        __dbt__cte__stg_calendar_hours A
        LEFT JOIN "orquest_db"."orquest_raw"."associations"
        b
        ON A.person_id = b.person_id
        AND A.day BETWEEN b.from_date
        AND b.to_date
)
SELECT
    day,
    person_id,
    worked_hours AS planned_hours,
    case when store_id is not null then 0 else 1 end as in_usual_store
    from joined