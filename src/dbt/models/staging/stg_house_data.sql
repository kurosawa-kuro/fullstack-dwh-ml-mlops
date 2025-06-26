{{
  config(
    materialized='table',
    schema='bronze'
  )
}}

-- Bronze layer: Raw house data from CSV seed
-- This model loads raw data directly from the CSV file using dbt seeds
SELECT 
    ROW_NUMBER() OVER (ORDER BY price) as id,  -- Generate surrogate key
    price,
    sqft,
    bedrooms,
    bathrooms,
    location,
    year_built,
    condition,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
FROM {{ ref('house_data') }} 