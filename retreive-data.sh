#!/bin/bash

ar=$(cat uk-counties-raw.json | jq -r '.[].fields.ctyua_code')

run_script() {
    curl "https://api.coronavirus.data.gov.uk/v2/data?areaType=utla&areaCode=${1}&metric=newCasesBySpecimenDate&metric=newDeaths28DaysByDeathDate&metric=newVirusTestsBySpecimenDate&format=csv" -o "${1}.csv"
    sleep 0.3
}
mkdir csvs
cd csvs

for i in $ar
do
    run_script $i
done
