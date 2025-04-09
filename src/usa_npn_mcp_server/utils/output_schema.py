"""Module for API output schemas for the NPN API."""

from typing import Any, Dict


API_SCHEMAS: Dict[str, Any] = {
    "observation-comment": {
        "type": "object",
        "properties": {
            "comment": {
                "type": "string",
                "description": "The comment associated with the observation.",
            },
        },
    },
    "status-intensity": {
        "type": "object",
        "properties": {
            "observation_id": {
                "type": "int",
                "description": "The unique identifier of each phenophase status record (subsequently referred to as 'status record') in the database.",
            },
            "dataset_id": {
                "type": "int",
                "description": "The unique identifier of the dataset to which the status record belongs. A value of '-9999' indicates the status record was submitted via the online Nature's Notebook application.",
            },
            "observedby_person_id": {
                "type": "int",
                "description": "The unique identifier of the person who made the status observation in the field. A value of '-1' indicates the identity of the observer is unknown.",
            },
            "submission_id": {
                "type": "int",
                "description": "The unique identifier of the set of status records originally submitted online in the same, single click of the 'Submit Observations' button, to which this status record belongs. A value of '-1' indicates the record was added to the database as part of an integrated dataset.",
            },
            "submittedby_person_id": {
                "type": "int",
                "description": "The unique identifier of the person who originally submitted the status record online. A value of '-1' indicates the record was added to the database as part of an integrated dataset.",
            },
            "submission_datetime": {
                "type": "string",
                "format": "date-time",
                "description": "The date and time that the status record was originally submitted to the database.",
            },
            "updatedby_person_id": {
                "type": "int",
                "description": "The unique identifier of the person who last updated the status record after original submission online. A value of '-9999' indicates the record has not been updated since this field was established in July 2014.",
            },
            "update_datetime": {
                "type": "string",
                "format": "date-time",
                "description": "The date and time the status record was last updated after original submission online. A value of '-9999' indicates the record has not been updated since this field was established in July 2014.",
            },
            "partner_group": {
                "type": "string",
                "description": "The name of the partner group with which the status record is associated. A value of '-9999' indicates the organism being monitored is not associated with a partner group.",
            },
            "site_id": {
                "type": "int",
                "description": "The unique identifier of the site at which the status record was made.",
            },
            "site_name": {
                "type": "string",
                "description": "The user-defined name of the site at which the status record was made.",
            },
            "latitude": {
                "type": "number",
                "description": "The latitude of the site at which the status record was made.",
            },
            "longitude": {
                "type": "number",
                "description": "The longitude of the site at which the status record was made.",
            },
            "elevation_in_meters": {
                "type": "number",
                "description": "The elevation (in meters) of the site at which the status record was made. A value of '-9999' indicates the elevation could not be calculated.",
            },
            "state": {
                "type": "string",
                "description": "The U.S. state or territory, Mexican state or Canadian province in which the site is located. A value of '-9999' indicates the site does not fall within the boundaries of North America.",
            },
            "species_id": {
                "type": "int",
                "description": "The unique identifier of the species for which the status record was made.",
            },
            "genus": {
                "type": "string",
                "description": "The taxonomic genus of the organism for which the status record was made.",
            },
            "species": {
                "type": "string",
                "description": "The taxonomic species of the organism for which the status record was made. In those rare cases where a taxonomic subspecies or varietal is designated, the subspecies or varietal name is appended to the species name after a hyphen (e.g. Cornus florida-appalachianspring).",
            },
            "common_name": {
                "type": "string",
                "description": "The common name of the species for which the status record was made. Common names for plants follow those in the USDA PLANTS Database (http://plants.usda.gov), and for animals, in the NatureServe database (http://explorer.natureserve.org).",
            },
            "kingdom": {
                "type": "string",
                "description": "The taxonomic kingdom of the organism for which the status record was made.",
                "enum": ["Plantae", "Animalia"],
            },
            "species_functional_type": {
                "type": "string",
                "description": "The plant ecological type or animal guild of the species for which the status record was made. These functional types are based on the species' phenology protocol assignment.",
                "enum": [
                    "Algae",
                    "Amphibian",
                    "Bird",
                    "Cactus",
                    "Deciduous broadleaf [tree or shrub]",
                    "Deciduous conifer",
                    "Evergreen broadleaf [tree or shrub]",
                    "Evergreen conifer",
                    "Fish",
                    "Forb",
                    "Graminoid [includes grasses, sedges and rushes]",
                    "Insect",
                    "Mammal",
                    "Reptile",
                    "Drought deciduous broadleaf [tree or shrub]",
                    "Pine",
                    "Semi-evergreen broadleaf [tree or shrub]",
                    "Evergreen forb",
                    "Semi-evergreen forb",
                ],
            },
            "species_category": {
                "type": "string",
                "description": "The categories (separated by commas) to which the species has been assigned.",
                "enum": [
                    "Allergen",
                    "Aquatic",
                    "Calibration",
                    "Cloned",
                    "Crop",
                    "Green Wave Campaign",
                    "Invasive",
                    "Ornamental",
                    "Nectar Connectors Campaign",
                    "Southwest Season Trackers Campaign",
                    "Shady Invaders Campaign",
                    "Flowers for Bats Campaign",
                ],
            },
            "lifecycle_duration": {
                "type": "string",
                "description": "The possible lifecycle durations of the species for which the status record was made.",
            },
            "growth_habit": {
                "type": "string",
                "description": "The possible growth habits of the species for which the status record was made.",
            },
            "usda_plants_symbol": {
                "type": "string",
                "description": "The USDA PLANTS Database (http://plants.usda.gov) symbol of the species for which the status record was made.",
            },
            "itis_number": {
                "type": "int",
                "description": "The Integrated Taxonomic Information System (http://itis.gov) taxonomic serial number of the species for which the status record was made.",
            },
            "individual_id": {
                "type": "int",
                "description": "The unique identifier of the individual plant or the animal species at a site for which the status record was made. Note that for plants, individuals are tracked separately, while for animals, the species as a whole (rather than unique individuals) is tracked at a site.",
            },
            "plant_nickname": {
                "type": "string",
                "description": "The user-defined nickname of the individual plant for which the status record was made. For animals, this field is populated with the species' common name.",
            },
            "patch": {
                "type": "int",
                "description": "For plants, indicates whether a delineated patch of many individual stems is the unit of observation instead of a single individual plant.",
                "enum": [1, 0],
            },
            "protocol_id": {
                "type": "int",
                "description": "The unique identifier of the protocol (i.e. the unique suite of phenophases) assigned to the species at the time the status observation was made in the field. More information can be found in the ancillary data files for 'Protocol' and 'Species Protocol'.",
            },
            "phenophase_id": {
                "type": "int",
                "description": "The unique identifier of the phenophase for which the status record was made. Note that there can be several names and definitions for a given phenophase as they vary between datasets and can change over time within datasets. All definitions lumped under the same Phenophase_ID are considered equivalent for the purposes of general phenological analysis.",
            },
            "phenophase_category": {
                "type": "string",
                "description": "The overarching life stage category of the phenophase for which the status record was made. Each category includes all phenophases across all plant or animal taxa that target that life stage.",
                "enum": [
                    "Leaves [for plants]",
                    "Flowers [for plants]",
                    "Fruits [for plants]",
                    "Needles [for plants]",
                    "Pollen cones [for plants]",
                    "Seed cones [for plants]",
                    "Activity [for animals]",
                    "Reproduction [for animals]",
                    "Development [for animals]",
                    "Method [for animals]",
                ],
            },
            "phenophase_description": {
                "type": "string",
                "description": "The descriptive title of the phenophase for which the status record was made. This is the overarching title of the phenophase defined by Phenophase_ID, and may include several different names and definitions (as defined in the Phenophase_Name and Phenophase_Definition_ID fields), as these vary between datasets and can change over time within datasets. More information can be found in the ancillary data file for 'Phenophase'.",
            },
            "phenophase_name": {
                "type": "string",
                "description": "The name used to describe the phenophase at the time the status observation was made in the field.",
            },
            "phenophase_definition_id": {
                "type": "int",
                "description": "The unique identifier of the descriptive definition used to define the phenophase at the time the status observation was made in the field.",
            },
            "species-specific_info_id": {
                "type": "int",
                "description": "The unique identifier of the record which includes species-specific information (additional, species-specific phenophase definition and/or intensity category) assigned to the phenophase for this species at the time the status observation was made in the field. A value of '-9999' indicates there was no species-specific information assigned to this phenophase for this species at the time the observation was made.",
            },
            "observation_date": {
                "type": "string",
                "description": "The date the status observation was made in the field.",
            },
            "observation_time": {
                "type": "string",
                "description": "The time of day the status observation was made in the field. A value of '0:00:00' indicates either that no time was specified, or that the time of midnight was reported.",
            },
            "day_of_year": {
                "type": "int",
                "description": "The day of year, ranging from 1 to 366, that the status observation was made in the field.",
            },
            "phenophase_status": {
                "type": "int",
                "description": "The status (i.e. presence or absence) of the phenophase at the time the observation was made in the field.",
                "enum": [1, 0, -1],
            },
            "intensity_category_id": {
                "type": "int",
                "description": "The unique identifier of the intensity category assigned to the phenophase for this species at the time the status observation was made in the field. Intensity measures allow reporting of the degree to which a phenophase is expressed. A value of '-9999' indicates there was no intensity category assigned to this phenophase for this species at the time the observation was made.",
            },
            "intensity_value": {
                "type": "number",
                "description": "The value reported in response to the intensity category question assigned to the phenophase for this species at the time the status observation was made in the field.",
            },
            "abundance_value": {
                "type": "number",
                "description": "Used only for animal observations, the value reported in response to the instruction, 'enter the number of individual animals observed in this phenophase'.",
            },
            "site_visit_id": {
                "type": "int",
                "description": "The unique identifier for the group of all status observations made at the site during the same visit.",
            },
            "observation_comments": {
                "type": "string",
                "description": "Comments from the observer about the individual plant or animal species at the time the status observation was made in the field.",
            },
            "observed_status_conflict_flag": {
                "type": "string",
                "description": "Indicates the presence and type of conflict (i.e. reported Phenophase_Status of both 'yes' and 'no' on the same observation date) between this and at least one other phenophase status record for this same individual plant or animal species at this site.",
                "enum": ["MultiObserver-StatusConflict", "OneObserver-StatusConflict"],
            },
        },
    },
    "magnitude-phenometrics": {
        "type": "object",
        "properties": {
            "species_id": {
                "type": "int",
                "description": "The unique identifier of the species for which the data were recorded.",
            },
            "genus": {
                "type": "string",
                "description": "The taxonomic genus of the organism for which the data were recorded. ",
            },
            "species": {
                "type": "string",
                "description": "The taxonomic species of the organism for which the data were recorded. In those rare cases where a taxonomic subspecies or varietal is designated, the subspecies or varietal name is appended to the species name after a hyphen (e.g. Cornus florida-appalachianspring).",
            },
            "common_name": {
                "type": "string",
                "description": "The common name of the species for which the data were recorded. Common names for plants follow those in the USDA PLANTS Database (http://plants.usda.gov), and for animals, in the NatureServe database (http://explorer.natureserve.org).",
            },
            "kingdom": {
                "type": "string",
                "description": "The taxonomic kingdom of the organism for which the data were recorded.",
                "enum": ["Plantae", "Animalia"],
            },
            "species_functional_type": {
                "type": "string",
                "description": "The plant ecological type or animal guild of the species for which the data were recorded.",
                "enum": [
                    "Algae",
                    "Amphibian",
                    "Bird",
                    "Cactus",
                    "Deciduous broadleaf [tree or shrub]",
                    "Deciduous conifer",
                    "Evergreen broadleaf [tree or shrub]",
                    "Evergreen conifer",
                    "Fish",
                    "Forb",
                    "Graminoid [includes grasses, sedges and rushes]",
                    "Insect",
                    "Mammal",
                    "Reptile",
                    "Drought deciduous broadleaf [tree or shrub]",
                    "Pine",
                    "Semi-evergreen broadleaf [tree or shrub]",
                    "Evergreen forb",
                    "Semi-evergreen forb",
                ],
            },
            "species_category": {
                "type": "string",
                "description": "The categories (separated by commas) to which the species has been assigned.",
                "enum": [
                    "Allergen",
                    "Aquatic",
                    "Calibration",
                    "Cloned",
                    "Crop",
                    "Green Wave Campaign",
                    "Invasive",
                    "Ornamental",
                    "Nectar Connectors Campaign",
                    "Southwest Season Trackers Campaign",
                    "Shady Invaders Campaign",
                    "Flowers for Bats Campaign",
                ],
            },
            "lifecycle_duration": {
                "type": "string",
                "description": "The possible lifecycle durations of the species for which the data were recorded.",
            },
            "growth_habit": {
                "type": "string",
                "description": "The possible growth habits of the species for which the data were recorded.",
            },
            "usda_plants_symbol": {
                "type": "string",
                "description": "The USDA PLANTS Database (http://plants.usda.gov) symbol of the species for which the data were recorded.",
            },
            "itis_number": {
                "type": "int",
                "description": "The Integrated Taxonomic Information System (http://itis.gov) taxonomic serial number of the species for which the data were recorded.",
            },
            "phenophase_id": {
                "type": "int",
                "description": "The unique identifier of the phenophase for which the data were recorded.",
            },
            "phenophase_category": {
                "type": "string",
                "description": "The overarching life stage category of the phenophase for which the data were recorded. Each category includes all phenophases across all plant or animal taxa that target that life stage.",
                "enum": [
                    "Leaves [for plants]",
                    "Flowers [for plants]",
                    "Fruits [for plants]",
                    "Needles [for plants]",
                    "Pollen cones [for plants]",
                    "Seed cones [for plants]",
                    "Activity [for animals]",
                    "Reproduction [for animals]",
                    "Development [for animals]",
                    "Method [for animals]",
                ],
            },
            "phenophase_description": {
                "type": "string",
                "description": "The descriptive title of the phenophase for which the data were recorded.",
            },
            "year": {
                "type": "int",
                "description": "The year of the time period selected for summarization.",
            },
            "start_date": {
                "type": "string",
                "format": "date",
                "description": "The first day of the time period selected for summarization.",
            },
            "start_date_doy": {
                "type": "int",
                "description": "The day of year, ranging from 1 to 366, of the first day of the time period selected for summarization.",
            },
            "end_date": {
                "type": "string",
                "format": "date",
                "description": "The last day of the time period selected for summarization.",
            },
            "end_date_doy": {
                "type": "int",
                "description": "The day of year, ranging from 1 to 366, of the last day of the time period selected for summarization.",
            },
            "status_records_sample_size": {
                "type": "int",
                "description": "The total number of 'yes' and 'no' status records for the species and phenophase within the selected time period.",
            },
            "individuals_sample_size": {
                "type": "int",
                "description": "The number of individuals with at least one 'yes' or 'no' status record for the species and phenophase within the selected time period.",
            },
            "sites_sample_size": {
                "type": "int",
                "description": "The number of sites with at least one 'yes' or 'no' status record for the species and phenophase within the selected time period.",
            },
            "num_yes_records": {
                "type": "int",
                "description": "The total number of 'yes' status records for the species and phenophase within the selected time period.",
            },
            "num_individuals_with_yes_record": {
                "type": "int",
                "description": "The number of individual plants with at least one 'yes' status record for the species and phenophase within the selected time period.",
            },
            "num_sites_with_yes_record": {
                "type": "int",
                "description": "The number of sites with at least one 'yes' status record for the species and phenophase within the selected time period. This metric is not calculated for plant species.",
            },
            "proportion_yes_records": {
                "type": "number",
                "description": "The number of 'yes' records divided by the total number of 'yes' and 'no' status records for the species and phenophase within the selected time period.",
            },
            "proportion_individuals_with_yes_record": {
                "type": "number",
                "description": "The number of individual plants with at least one 'yes' record, divided by the number of individuals with any 'yes' or 'no' status records for the species and phenophase within the selected time period.",
            },
            "proportion_sites_with_yes_record": {
                "type": "number",
                "description": "The number of sites with at least one 'yes' record, divided by the number of sites with any 'yes' or 'no' status records for the species and phenophase within the selected time period.",
            },
            "in-phase_search_method": {
                "type": "string",
                "description": "The search method(s) (separated by commas) used to collect the records which contribute to the calculation of Total_NumAnimals_In-Phase and Mean_NumAnimals_In-Phase.",
                "enum": [
                    "Incidental [described as 'chance sighting while not specifically searching']",
                    "Stationary [described as 'standing or sitting at a single point']",
                    "Walking [described as 'a single pass or transect through your site']",
                    "Area Search [described as 'multiple passes through your site']",
                ],
            },
            "in-phase_sites_sample_size": {
                "type": "int",
                "description": "The number of sites which contribute records to the calculation of Total_NumAnimals_In-Phase and Mean_NumAnimals_In-Phase.",
            },
            "in-phase_site_visits_sample_size": {
                "type": "int",
                "description": "The number of site visits included in the calculation of Total_NumAnimals_In-Phase and Mean_NumAnimals_In-Phase.",
            },
            "total_num_animals_in-phase": {
                "type": "int",
                "description": "The sum of animal abundance from each site visit for the species and phenophase within the selected time period. Records with a phenophase status of 'uncertain' are not included in the calculation.",
            },
            "mean_num_animals_in-phase": {
                "type": "number",
                "description": "The mean of animal abundance from each site visit for the species and phenophase within the selected time period. 'No' records are assigned an abundance of zero. 'Yes' records with no abundance reported and records with a status of 'uncertain' are not included in the calculation.",
            },
            "se_num_animals_in-phase": {
                "type": "number",
                "description": "Standard error of the calculated Mean_NumAnimals_In-Phase.",
            },
            "sd_num_animals_in-phase": {
                "type": "number",
                "description": "Standard deviation of the calculated Mean_NumAnimals_In-Phase.",
            },
            "in-phase_per_hr_search_method": {
                "type": "string",
                "description": "The search method(s) (separated by commas) used to collect the records which contribute to the calculation of Mean_NumAnimals_In-Phase_per_Hr.",
                "enum": [
                    "Stationary [described as 'standing or sitting at a single point']",
                    "Walking [described as 'a single pass or transect through your site']",
                    "Area Search [described as 'multiple passes through your site']",
                ],
            },
            "in-phase_per_hr_sites_sample_size": {
                "type": "int",
                "description": "The number of sites which contribute records to the calculation of Mean_NumAnimals_In-Phase_per_Hr.",
            },
            "in-phase_per_hr_site_visits_sample_size": {
                "type": "int",
                "description": "The number of site visits included in the calculation of Mean_NumAnimals_In-Phase_per_Hr.",
            },
            "mean_num_animals_in-phase_per_hr": {
                "type": "number",
                "description": "The mean of animal abundance divided by the time spent searching for animals at each site visit (i.e. [Sum (abundance/time)]/# site visits) for the species and phenophase within the selected time period. Records with a 'no' phenophase status are assigned an abundance of zero. Records with a 'yes' phenophase status and no abundance reported, or with an 'uncertain' phenophase status, are not included. Site visits with any of the following conditions are excluded from the calculation: a search method of 'Incidental'; no search method reported; no search time reported; a reported search time greater than 180 minutes.",
            },
            "se_num_animals_in-phase_per_hr": {
                "type": "number",
                "description": "Standard error of the calculated Mean_NumAnimals_In-Phase_per_Hr.",
            },
            "sd_num_animals_in-phase_per_hr": {
                "type": "number",
                "description": "Standard deviation of the calculated Mean_NumAnimals_In-Phase_per_Hr.",
            },
            "in-phase_per_hr_per_acre_sites_sample_size": {
                "type": "int",
                "description": "The number of sites which contribute records to the calculation of Mean_NumAnimals_In-Phase_per_Hr_per_Acre.",
            },
            "in-phase_per_hr_per_acre_site_visits_sample_size": {
                "type": "int",
                "description": "The number of site visits included in the calculation of Mean_NumAnimals_In-Phase_per_Hr_per_Acre.",
            },
            "mean_num_animals_in-phase_per_hr_per_acre": {
                "type": "number",
                "description": "The mean of animal abundance divided by site area and divided by time spent searching for animals at each site visit (i.e. {Sum [(abundance/area)/time]}/# site visits) for the species and phenophase within the selected time period. Records with a 'no' phenophase status are assigned an abundance of zero. Records with a 'yes' phenophase status and no abundance reported, or with an 'uncertain' phenophase status, are not included. Site visits with any of the following conditions are excluded from the calculation: a search method of anything besides 'Area search'; no search time reported; a reported search time greater than 180 minutes; no reported area for the site.",
            },
            "se_num_animals_in-phase_per_hr_per_acre": {
                "type": "number",
                "description": "Standard error of the calculated Mean_NumAnimals_In-Phase_per_Hr_per_Acre.",
            },
            "sd_num_animals_in-phase_per_hr_per_acre": {
                "type": "number",
                "description": "Standard deviation of the calculated Mean_NumAnimals_In-Phase_per_Hr_per_Acre.",
            },
        },
    },
    "site-phenometrics": {
        "type": "object",
        "properties": {
            "partner_group": {
                "type": "string",
                "description": "The name of the partner group with which the data are associated. A value of '-9999' indicates the organism being monitored is not associated with a partner group.",
            },
            "site_id": {
                "type": "int",
                "description": "The unique identifier of the site at which the data were recorded.",
            },
            "site_name": {
                "type": "string",
                "description": "The user-defined name of the site at which the data were recorded.",
            },
            "latitude": {
                "type": "number",
                "description": "The latitude of the site at which the data were recorded.",
            },
            "longitude": {
                "type": "number",
                "description": "The longitude of the site at which the data were recorded.",
            },
            "elevation_in_meters": {
                "type": "number",
                "description": "The elevation (in meters) of the site at which the data were recorded. A value of '-9999' indicates the elevation could not be calculated.",
            },
            "state": {
                "type": "string",
                "description": "The U.S. state or territory, Mexican state or Canadian province in which the site is located. A value of '-9999' indicates the site does not fall within the boundaries of North America.",
            },
            "species_id": {
                "type": "int",
                "description": "The unique identifier of the species for which the data were recorded.",
            },
            "genus": {
                "type": "string",
                "description": "The taxonomic genus of the organism for which the data were recorded.",
            },
            "species": {
                "type": "string",
                "description": "The taxonomic species of the organism for which the data were recorded. In those rare cases where a taxonomic subspecies or varietal is designated, the subspecies or varietal name is appended to the species name after a hyphen (e.g. Cornus florida-appalachianspring).",
            },
            "common_name": {
                "type": "string",
                "description": "The common name of the species for which the data were recorded. Common names for plants follow those in the USDA PLANTS Database (http://plants.usda.gov), and for animals, in the NatureServe database (http://explorer.natureserve.org).",
            },
            "kingdom": {
                "type": "string",
                "description": "The taxonomic kingdom of the organism for which the data were recorded.",
                "enum": ["Plantae", "Animalia"],
            },
            "species_functional_type": {
                "type": "string",
                "description": "The plant ecological type or animal guild of the species for which the data were recorded. These functional types are based on the species' phenology protocol assignment, and in a few cases do not correspond with a plant species' established botanical classification (e.g. sub-shrubs that grow more like forbs because woody parts are belowground).",
                "enum": [
                    "Algae",
                    "Amphibian",
                    "Bird",
                    "Cactus",
                    "Deciduous broadleaf [tree or shrub]",
                    "Deciduous conifer",
                    "Evergreen broadleaf [tree or shrub]",
                    "Evergreen conifer",
                    "Fish",
                    "Forb",
                    "Graminoid [includes grasses, sedges and rushes]",
                    "Insect",
                    "Mammal",
                    "Reptile",
                    "Drought deciduous broadleaf [tree or shrub]",
                    "Pine",
                    "Semi-evergreen broadleaf [tree or shrub]",
                    "Evergreen forb",
                    "Semi-evergreen forb",
                ],
            },
            "species_category": {
                "type": "string",
                "description": "The categories (separated by commas) to which the species has been assigned.",
                "enum": [
                    "Allergen",
                    "Aquatic",
                    "Calibration",
                    "Cloned",
                    "Crop",
                    "Green Wave Campaign",
                    "Invasive",
                    "Ornamental",
                    "Nectar Connectors Campaign",
                    "Southwest Season Trackers Campaign",
                    "Shady Invaders Campaign",
                    "Flowers for Bats Campaign",
                ],
            },
            "lifecycle_duration": {
                "type": "string",
                "description": "The possible lifecycle durations of the species for which the data were recorded.",
            },
            "growth_habit": {
                "type": "string",
                "description": "The possible growth habits of the species for which the data were recorded.",
            },
            "usda_plants_symbol": {
                "type": "string",
                "description": "The USDA PLANTS Database (http://plants.usda.gov) symbol of the species for which the data were recorded.",
            },
            "itis_number": {
                "type": "int",
                "description": "The Integrated Taxonomic Information System (http://itis.gov) taxonomic serial number of the species for which the data were recorded.",
            },
            "phenophase_id": {
                "type": "int",
                "description": "The unique identifier of the phenophase for which the data were recorded.",
            },
            "phenophase_category": {
                "type": "string",
                "description": "The overarching life stage category of the phenophase for which the data were recorded. Each category includes all phenophases across all plant or animal taxa that target that life stage.",
                "enum": [
                    "Leaves [for plants]",
                    "Flowers [for plants]",
                    "Fruits [for plants]",
                    "Needles [for plants]",
                    "Pollen cones [for plants]",
                    "Seed cones [for plants]",
                    "Activity [for animals]",
                    "Reproduction [for animals]",
                    "Development [for animals]",
                    "Method [for animals]",
                ],
            },
            "phenophase_description": {
                "type": "string",
                "description": "The descriptive title of the phenophase for which the data were recorded.",
            },
            "first_yes_sample_size": {
                "type": "int",
                "description": "The number of individual organisms that contribute a first 'yes' record to calculation of Mean_First_Yes_DOY and Mean_First_Yes_Julian_Date. Individual animals are not monitored separately, rather the species as a whole is monitored at a site, so this value will always be '1' for animal species.",
            },
            "mean_first_yes_year": {
                "type": "int",
                "description": "The year of the calculated Mean_First_Yes_DOY.",
            },
            "mean_first_yes_doy": {
                "type": "int",
                "description": "The mean day of year, ranging from 1 to 366, of the first 'yes' phenophase status record(s) for the species at the site within the selected time period. The 'Data Precision Filter' requires users to exclude 'yes' records not preceded by a 'no' record within 7, 14 or 30 days during the selected time period.",
            },
            "mean_first_yes_julian_date": {
                "type": "int",
                "description": "The mean astronomical Julian date of the first 'yes' phenophase status record(s) for the species at the site within the selected time period (calculated as days and hours since noon on January 1, 4713 BC in the proleptic Julian calendar). Decimal values are truncated (rounded down) to the nearest whole number so they represent noon of the calendar day. The 'Data Precision Filter' requires users to exclude 'yes' records not preceded by a 'no' record within 7, 14 or 30 days during the selected time period.",
            },
            "se_first_yes_in_days": {
                "type": "int",
                "description": "Standard error (in days) of the calculated Mean_First_Yes_DOY. A value of '-9999' indicates that the first 'yes' record of only one individual was used in the calculation. A value of '0' indicates that the first 'yes' records of multiple individuals where used in the calculation and all occurred on the same day.",
            },
            "sd_first_yes_in_days": {
                "type": "int",
                "description": "Standard deviation (in days) of the calculated Mean_First_Yes_DOY. A value of '-9999' indicates that the first 'yes' record of only one individual was used in the calculation. A value of '0' indicates that the first 'yes' records of multiple individuals where used in the calculation and all occurred on the same day.",
            },
            "min_first_yes_doy": {
                "type": "int",
                "description": "The day of year (ranging from 1 to 366) of the earliest first 'yes' record used in the calculation of Mean_First_Yes_DOY.",
            },
            "max_first_yes_doy": {
                "type": "int",
                "description": "The day of year (ranging from 1 to 366) of the latest first 'yes' record used in the calculation of Mean_First_Yes_DOY.",
            },
            "median_first_yes_doy": {
                "type": "int",
                "description": "The median day of year (ranging from 1 to 366) of the first 'yes' records used in the calculation of Mean_First_Yes_DOY.",
            },
            "mean_numdays_since_prior_no": {
                "type": "int",
                "description": "Mean of the number of days between the first 'yes' phenophase status record and the last prior 'no' phenophase status record for each individual used in the calculation of Mean_First_Yes_DOY.",
            },
            "se_numdays_since_prior_no": {
                "type": "int",
                "description": "Standard error (in days) of the calculated Mean_NumDays_Since_Prior_No. A value of '-9999' indicates that the first 'yes' and prior 'no' records of only one individual were used in the calculation. A value of '0' indicates that the first 'yes' and prior 'no' records of multiple individuals where used in the calculation and each set of records had the same number of days between them.",
            },
            "sd_numdays_since_prior_no": {
                "type": "int",
                "description": "Standard deviation (in days) of the calculated Mean_NumDays_Since_Prior_No. A value of '-9999' indicates that the first 'yes' and prior 'no' records of only one individual were used in the calculation. A value of '0' indicates that the first 'yes' and prior 'no' records of multiple individuals where used in the calculation and each set of records had the same number of days between them.",
            },
            "last_yes_sample_size": {
                "type": "int",
                "description": "The number of individual organisms that contribute a last 'yes' record to calculation of Mean_Last_Yes_DOY and Mean_Last_Yes_Julian_Date. Individual animals are not monitored separately, rather the species as a whole is monitored at a site, so this value will always be '1' for animal species.",
            },
            "mean_last_yes_year": {
                "type": "int",
                "description": "The year of the calculated Mean_Last_Yes_DOY.",
            },
            "mean_last_yes_doy": {
                "type": "int",
                "description": "The mean day of year, ranging from 1 to 366, of the last 'yes' phenophase status record(s) for the species at the site within the selected time period. The 'Data Precision Filter' requires users to exclude 'yes' records not followed by a 'no' record within 7, 14 or 30 days during the selected time period.",
            },
            "mean_last_yes_julian_date": {
                "type": "int",
                "description": "The mean astronomical Julian date of the last 'yes' phenophase status record(s) for the species at the site within the selected time period (calculated as days and hours since noon on January 1, 4713 BC in the proleptic Julian calendar). Decimal values are truncated (rounded down) to the nearest whole number so they represent noon of the calendar day. The 'Data Precision Filter' requires users to exclude 'yes' records not followed by a 'no' record within 7, 14 or 30 days during the selected time period.",
            },
            "se_last_yes_in_days": {
                "type": "int",
                "description": "Standard error (in days) of the calculated Mean_Last_Yes_DOY. A value of '-9999' indicates that the last 'yes' record of only one individual was used in the calculation. A value of '0' indicates that the last 'yes' records of multiple individuals where used in the calculation and all occurred on the same day.",
            },
            "sd_last_yes_in_days": {
                "type": "int",
                "description": "Standard deviation (in days) of the calculated Mean_Last_Yes_DOY. A value of '-9999' indicates that the last 'yes' record of only one individual was used in the calculation. A value of '0' indicates that the last 'yes' records of multiple individuals where used in the calculation and all occurred on the same day.",
            },
            "min_last_yes_doy": {
                "type": "int",
                "description": "The day of year (ranging from 1 to 366) of the earliest last 'yes' record used in the calculation of Mean_Last_Yes_DOY.",
            },
            "max_last_yes_doy": {
                "type": "int",
                "description": "The day of year (ranging from 1 to 366) of the latest last 'yes' record used in the calculation of Mean_Last_Yes_DOY.",
            },
            "median_last_yes_doy": {
                "type": "int",
                "description": "The median day of year (ranging from 1 to 366) of the last 'yes' records used in the calculation of Mean_Last_Yes_DOY.",
            },
            "mean_numdays_until_next_no": {
                "type": "int",
                "description": "Mean of the number of days between the last 'yes' phenophase status record and the next 'no' phenophase status record for each individual used in the calculation of Mean_Last_Yes_DOY.",
            },
            "se_numdays_until_next_no": {
                "type": "int",
                "description": "Standard error (in days) of the calculated Mean_NumDays_Until_Next_No. A value of '-9999' indicates that the last 'yes' and next 'no' records of only one individual were used in the calculation. A value of '0' indicates that the last 'yes' and next 'no' records of multiple individuals where used in the calculation and each set of records had the same number of days between them.",
            },
            "sd_numdays_until_next_no": {
                "type": "int",
                "description": "Standard deviation (in days) of the calculated Mean_NumDays_Until_Next_No. A value of '-9999' indicates that the last 'yes' and next 'no' records of only one individual were used in the calculation. A value of '0' indicates that the last 'yes' and next 'no' records of multiple individuals where used in the calculation and each set of records had the same number of days between them.",
            },
            "num_individuals_with_multiple_firsty": {
                "type": "int",
                "description": "The number of individuals used in the calculation of 'Mean First Yes' or 'Mean Last Yes' that have more than one discrete period of activity for the phenophase within the selected time period. These separate periods of activity (called 'series') can be explored in our individual phenometrics data type. When the selected time period consists of more than one year, calculation of multiple periods of activity is separate for each 12-month time span starting from the selected start date.",
            },
            "multiple_firsty_individual_ids": {
                "type": "string",
                "description": "For plant species, the Individual_ID numbers (separated by commas) of the individual plants with 'Multiple FirstY'.",
            },
            "observed_status_conflict_flag": {
                "type": "string",
                "description": "Indicates the presence and type of conflict (i.e. reported Phenophase_Status of both 'yes' and 'no' on the same observation date for the same individual plant or animal species at a site) between two or more phenophase status records used in the calculation of 'Mean First Yes' or 'Mean Last Yes'. These conflicts can be explored in our status and intensity data type.",
                "enum": ["MultiObserver-StatusConflict", "OneObserver-StatusConflict"],
            },
            "observed_status_conflict_flag_individual_ids": {
                "type": "string",
                "description": "The Individual_ID number(s) (separated by commas) of the organism(s) with an 'Observed Status Conflict'.",
            },
            "mean_agdd": {
                "type": "number",
                "description": "Mean of the accumulated growing degree days (in degrees C) on the date of each first 'yes' record included in the calculation of Mean_First_Yes_DOY and Mean_First_Yes_Julian_Date. AGDD is the sum of growing degree days (GDD) since January 1st, where GDD is calculated as the number of degrees C by which each day's average temperature exceeds 0 degrees C (i.e., (Tmax + Tmin)/2 - 0 degrees C).",
            },
            "mean_agdd_in_f": {
                "type": "number",
                "description": "Mean of the accumulated growing degree days (in degrees F) on the date of each first 'yes' record included in the calculation of Mean_First_Yes_DOY and Mean_First_Yes_Julian_Date. AGDD is the sum of growing degree days (GDD) since January 1st, where GDD is calculated as the number of degrees F by which each day's average temperature exceeds 32 degrees F (i.e., (Tmax + Tmin)/2 - 32 degrees F).",
            },
            "se_agdd": {
                "type": "number",
                "description": "Standard error (in degrees C) of the calculated Mean_AGDD. A value of '-9999' indicates that the AGDD for only one date was used in the calculation. A value of '0' indicates that the AGDD for two or more dates where used in the calculation and each date had the same AGDD value.",
            },
            "se_agdd_in_f": {
                "type": "number",
                "description": "Standard error (in degrees F) of the calculated Mean_AGDD. A value of '-9999' indicates that the AGDD for only one date was used in the calculation. A value of '0' indicates that the AGDD for two or more dates where used in the calculation and each date had the same AGDD value.",
            },
            "tmax_winter": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the winter season of Mean_First_Yes_Year (December of previous year to February of Mean_First_Yes_Year).",
            },
            "tmax_spring": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the spring season of Mean_First_Yes_Year (March-May).",
            },
            "tmax_summer": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the summer season of Mean_First_Yes_Year (June-August).",
            },
            "tmax_fall": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the previous year's fall season (September-November), relative to Mean_First_Yes_Year.",
            },
            "tmin_winter": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the winter season of Mean_First_Yes_Year (December of previous year to February of Mean_First_Yes_Year).",
            },
            "tmin_spring": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the spring season of Mean_First_Yes_Year (March-May).",
            },
            "tmin_summer": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the summer season of Mean_First_Yes_Year (June-August).",
            },
            "tmin_fall": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the previous year's fall season (September-November), relative to Mean_First_Yes_Year.",
            },
            "prcp_winter": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the winter season of Mean_First_Yes_Year (December of previous year to February of Mean_First_Yes_Year).",
            },
            "prcp_spring": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the spring season of Mean_First_Yes_Year (March-May).",
            },
            "prcp_summer": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the summer season of Mean_First_Yes_Year (June-August).",
            },
            "prcp_fall": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the previous year's fall season (September-November), relative to Mean_First_Yes_Year.",
            },
            "mean_accum_prcp": {
                "type": "number",
                "description": "Mean of accumulated precipitation (in mm since January 1st) on the date of each first 'yes' record included in the calculation of Mean_First_Yes_DOY and Mean_First_Yes_Julian_Date.",
            },
            "se_accum_prcp": {
                "type": "number",
                "description": "Standard error (in mm) of the calculated Mean_Accum_Prcp. A value of '-9999' indicates that the accumulated precipitation for only one date was used in the calculation. A value of '0' indicates that the accumulated precipitation for two or more dates where used in the calculation and each date had the same accumulated precipitation value.",
            },
            "mean_daylength": {
                "type": "number",
                "description": "Mean of the number of seconds of daylight on the date of each first 'yes' record included in the calculation of Mean_First_Yes_DOY and Mean_First_Yes_Julian_Date.",
            },
            "se_daylength": {
                "type": "number",
                "description": "Standard error of the calculated Mean_Daylength. A value of '-9999' indicates that the daylength for only one date was used in the calculation. A value of '0' indicates that the daylength for two or more dates where used in the calculation and each date had the same daylength value.",
            },
        },
    },
    "individual-phenometrics": {
        "type": "object",
        "properties": {
            "dataset_id": {
                "type": "int",
                "description": "The unique identifiers of the dataset(s) (separated by commas) to which the status records that constitute the series belong. A value of '-9999' indicates one or more status records were submitted via the online Nature's Notebook application.",
            },
            "observedby_person_id": {
                "type": "int",
                "description": "The unique identifiers of the person(s) (separated by commas) who made the status observations that constitute the series. A value of '-1' indicates the identity of the observer is unknown.",
            },
            "partner_group": {
                "type": "string",
                "description": "The name of the partner group with which the series is associated. A value of '-9999' indicates the organism being monitored is not associated with a partner group.",
            },
            "site_id": {
                "type": "int",
                "description": "The unique identifier of the site at which the series was recorded. More information can be found in the ancillary data file for 'Site'.",
            },
            "site_name": {
                "type": "string",
                "description": "The user-defined name of the site at which the series was recorded.",
            },
            "latitude": {
                "type": "number",
                "description": "The latitude of the site at which the series was recorded.",
            },
            "longitude": {
                "type": "number",
                "description": "The longitude of the site at which the series was recorded.",
            },
            "elevation_in_meters": {
                "type": "number",
                "description": "The elevation (in meters) of the site at which the series was recorded. A value of '-9999' indicates the elevation could not be calculated.",
            },
            "state": {
                "type": "string",
                "description": "The U.S. state or territory, Mexican state or Canadian province in which the site is located. A value of '-9999' indicates the site does not fall within the boundaries of North America.",
            },
            "species_id": {
                "type": "int",
                "description": "The unique identifier of the species for which the series was recorded.",
            },
            "genus": {
                "type": "string",
                "description": "The taxonomic genus of the organism for which the series was recorded.",
            },
            "species": {
                "type": "string",
                "description": "The taxonomic species of the organism for which the series was recorded. In those rare cases where a taxonomic subspecies or varietal is designated, the subspecies or varietal name is appended to the species name after a hyphen (e.g. Cornus florida-appalachianspring).",
            },
            "common_name": {
                "type": "string",
                "description": "The common name of the species for which the series was recorded. Common names for plants follow those in the USDA PLANTS Database (http://plants.usda.gov), and for animals, in the NatureServe database (http://explorer.natureserve.org).",
            },
            "kingdom": {
                "type": "string",
                "description": "The taxonomic kingdom of the organism for which the series was recorded.",
                "enum": ["Plantae", "Animalia"],
            },
            "species_functional_type": {
                "type": "string",
                "description": "The plant ecological type or animal guild of the species for which the series was recorded. These functional types are based on the species' phenology protocol assignment, and in a few cases do not correspond with a plant species' established botanical classification (e.g. sub-shrubs that grow more like forbs because woody parts are belowground).",
                "enum": [
                    "Algae",
                    "Amphibian",
                    "Bird",
                    "Cactus",
                    "Deciduous broadleaf [tree or shrub]",
                    "Deciduous conifer",
                    "Evergreen broadleaf [tree or shrub]",
                    "Evergreen conifer",
                    "Fish",
                    "Forb",
                    "Graminoid [includes grasses, sedges and rushes]",
                    "Insect",
                    "Mammal",
                    "Reptile",
                    "Drought deciduous broadleaf [tree or shrub]",
                    "Pine",
                    "Semi-evergreen broadleaf [tree or shrub]",
                    "Evergreen forb",
                    "Semi-evergreen forb",
                ],
            },
            "species_category": {
                "type": "string",
                "description": "The categories (separated by commas) to which the species has been assigned.",
                "enum": [
                    "Allergen",
                    "Aquatic",
                    "Calibration",
                    "Cloned",
                    "Crop",
                    "Green Wave Campaign",
                    "Invasive",
                    "Ornamental",
                    "Nectar Connectors Campaign",
                    "Southwest Season Trackers Campaign",
                    "Shady Invaders Campaign",
                    "Flowers for Bats Campaign",
                ],
            },
            "lifecycle_duration": {
                "type": "string",
                "description": "The possible lifecycle durations of the species for which the series was recorded.",
            },
            "growth_habit": {
                "type": "string",
                "description": "The possible growth habits of the species for which the series was recorded.",
            },
            "usda_plants_symbol": {
                "type": "string",
                "description": "The USDA PLANTS Database (http://plants.usda.gov) symbol of the species for which the series was recorded.",
            },
            "itis_number": {
                "type": "int",
                "description": "The Integrated Taxonomic Information System (http://itis.gov) taxonomic serial number of the species for which the series was recorded.",
            },
            "individual_id": {
                "type": "int",
                "description": "The unique identifier of the individual plant or the animal species at a site for which the series was recorded. Note that for plants, individuals are tracked separately, while for animals, the species as a whole (rather than unique individuals) is tracked at a site.",
            },
            "plant_nickname": {
                "type": "string",
                "description": "The user-defined nickname of the individual plant for which the series was recorded. For animals, this field is populated with the species' common name.",
            },
            "patch": {
                "type": "int",
                "description": "For plants, indicates whether a delineated patch of many individual stems is the unit of observation instead of a single individual plant.",
                "enum": [1, 0],
            },
            "phenophase_id": {
                "type": "int",
                "description": "The unique identifier of the phenophase for which the series was recorded.",
            },
            "phenophase_category": {
                "type": "string",
                "description": "The overarching life stage category of the phenophase for which the series was recorded. Each category includes all phenophases across all plant or animal taxa that target that life stage.",
                "enum": [
                    "Leaves [for plants]",
                    "Flowers [for plants]",
                    "Fruits [for plants]",
                    "Needles [for plants]",
                    "Pollen cones [for plants]",
                    "Seed cones [for plants]",
                    "Activity [for animals]",
                    "Reproduction [for animals]",
                    "Development [for animals]",
                    "Method [for animals]",
                ],
            },
            "phenophase_description": {
                "type": "string",
                "description": "The descriptive title of the phenophase for which the series was recorded.",
            },
            "first_yes_year": {
                "type": "int",
                "description": "The year of the first 'yes' record of the series.",
            },
            "first_yes_month": {
                "type": "int",
                "description": "The month of the first 'yes' record of the series.",
            },
            "first_yes_day": {
                "type": "int",
                "description": "The day of the month of the first 'yes' record of the series.",
            },
            "first_yes_doy": {
                "type": "int",
                "description": "The day of year, ranging from 1 to 366, of the first 'yes' record of the series.",
            },
            "first_yes_julian_date": {
                "type": "int",
                "description": "The astronomical Julian date of the first 'yes' record of the series (calculated as days and hours since noon on January 1, 4713 BC in the proleptic Julian calendar). Decimal values are truncated (rounded down) to the nearest whole number so they represent noon of the calendar day the observation was made.",
            },
            "numdays_since_prior_no": {
                "type": "int",
                "description": "The number of days between the last 'no' phenophase status record and the first 'yes' phenophase status record of the series. A value of '-9999' indicates there was not a 'no' record preceding the first 'yes' record of the series within the selected time period.",
            },
            "last_yes_year": {
                "type": "int",
                "description": "The year of the last 'yes' record of the series.",
            },
            "last_yes_month": {
                "type": "int",
                "description": "The month of the last 'yes' record of the series.",
            },
            "last_yes_day": {
                "type": "int",
                "description": "The day of the month of the last 'yes' record of the series.",
            },
            "last_yes_doy": {
                "type": "int",
                "description": "The day of year, ranging from 1 to 366, of the last 'yes' record of the series.",
            },
            "last_yes_julian_date": {
                "type": "int",
                "description": "The astronomical Julian date of the last 'yes' record of the series (calculated as days and hours since noon on January 1, 4713 BC in the proleptic Julian calendar). Decimal values are truncated (rounded down) to the nearest whole number so they represent noon of the calendar day the observation was made.",
            },
            "numdays_until_next_no": {
                "type": "int",
                "description": "The number of days between the last 'yes' phenophase status record of the series and the next 'no' phenophase status record. A value of '-9999' indicates there was not a 'no' record following the last 'yes' record of the series within the selected time period.",
            },
            "numys_in_series": {
                "type": "int",
                "description": "The total number of days in the series with a 'yes' record.",
            },
            "numdays_in_series": {
                "type": "int",
                "description": "The total number of days in the series.",
            },
            "multiple_observers": {
                "type": "int",
                "description": "Indicates whether multiple observers contributed records to the series. A value of '0' indicates only one observer contributed records, and a value of '1' indicates more than one observer contributed records.",
            },
            "multiple_firsty": {
                "type": "int",
                "description": "Indicates whether there are multiple series for the phenophase on the organism within the selected time period. A value of '0' indicates there is only one series, and a value of '1' indicates there are more than one series within the selected time period. When the selected time period consists of more than one year, calculation of multiple series is separate for each 12-month time span starting from the selected start date. Note that the first 'yes' record for a 12-month time span during the selected time period might not be preceded by a 'no' record, but the first 'yes' for subsequent series within the same 12-month time span is always separated from the previous series by at least one 'no' record.",
            },
            "observed_status_conflict_flag": {
                "type": "string",
                "description": "Indicates the presence and type of conflict (i.e. reported Phenophase_Status of both 'yes' and 'no' for the same observation date) between two or more phenophase status records included in the series.",
                "enum": ["MultiObserver-StatusConflict", "OneObserver-StatusConflict"],
            },
            "agdd": {
                "type": "number",
                "description": "Accumulated growing degree days (in degrees Celsius) on the date of the first 'yes' record of the series. This is the sum of growing degree days (GDD) since January 1st, where GDD is calculated as the number of degrees C by which each day's average temperature exceeds 0 degrees C (i.e., (Tmax + Tmin)/2 - 0 degrees C).",
            },
            "agdd_in_f": {
                "type": "number",
                "description": "Accumulated growing degree days (in degrees Fahrenheit) on the date of the first 'yes' record of the series. This is the sum of growing degree days (GDD) since January 1st, where GDD is calculated as the number of degrees F by which each day's average temperature exceeds 32 degrees F (i.e., (Tmax + Tmin)/2 - 32 degrees F).",
            },
            "tmax_winter": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the winter season of First_Yes_Year (December of previous year to February of First_Yes_Year).",
            },
            "tmax_spring": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the spring season of First_Yes_Year (March-May).",
            },
            "tmax_summer": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the summer season of First_Yes_Year (June-August).",
            },
            "tmax_fall": {
                "type": "number",
                "description": "Average maximum temperature (in degrees C) for the previous year's fall season (September-November), relative to First_Yes_Year.",
            },
            "tmin_winter": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the winter season of First_Yes_Year (December of previous year to February of First_Yes_Year).",
            },
            "tmin_spring": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the spring season of First_Yes_Year (March-May).",
            },
            "tmin_summer": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the summer season of First_Yes_Year (June-August).",
            },
            "tmin_fall": {
                "type": "number",
                "description": "Average minimum temperature (in degrees C) for the previous year's fall season (September-November), relative to First_Yes_Year.",
            },
            "prcp_winter": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the winter season of First_Yes_Year (December of previous year to February of First_Yes_Year).",
            },
            "prcp_spring": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the spring season of First_Yes_Year (March-May).",
            },
            "prcp_summer": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the summer season of First_Yes_Year (June-August).",
            },
            "prcp_fall": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) for the previous year's fall season (September-November), relative to First_Yes_Year.",
            },
            "accum_prcp": {
                "type": "number",
                "description": "Accumulated precipitation (in mm) from January 1st to the date of the first 'yes' record of the series.",
            },
            "daylength": {
                "type": "number",
                "description": "Number of seconds of daylight on the date of the first 'yes' record of the series.",
            },
        },
    },
}
