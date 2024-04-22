
select day, person_id, sum(worked_hours) as worked_hours
 from "orquest_db"."orquest_raw"."hours"
 group by day, person_id order by day, person_id