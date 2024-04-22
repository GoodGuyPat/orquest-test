
-- Include incidence data in order to account for absences

WITH  __dbt__cte__stg_calendar_hours as (

select day, person_id, sum(worked_hours) as worked_hours
 from "orquest_db"."orquest_raw"."hours"
 group by day, person_id order by day, person_id
),  __dbt__cte__stg_calendar_shop as (

-- Each planned date must fall within an association which has a store assigned to it.
-- Since multiple associations may be valid at once (in which case one exists as an
-- interruption inside another), we will only use the latest active for any given day.
WITH joined AS (
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
), joined AS (

    SELECT
        A.*,
        b.type_name,
        CASE
            WHEN b.type_name IS NULL THEN 0
            ELSE 1
        END AS is_absent
    FROM
        __dbt__cte__stg_calendar_shop A
        LEFT JOIN "orquest_db"."orquest_raw"."incidences"
        b
        ON A.person_id = b.person_id
        AND A.day BETWEEN b.from_date
        -- We coalesce with current_date to validate incidences with no end date
        AND coalesce(b.to_date, current_date)
)
SELECT
    *,
    case when is_absent = 0 then planned_hours else 0 end AS worked_hours
FROM
    joined