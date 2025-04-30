
MERGE INTO books_silver
USING (
    SELECT 
        updates.book_id AS merge_key, 
        updates.*
    FROM updates

    UNION ALL

    SELECT 
        NULL AS merge_key, 
        updates.*
    FROM updates
    JOIN books_silver 
      ON updates.book_id = books_silver.book_id
    WHERE 
        books_silver.current = true 
        AND updates.price <> books_silver.price
) staged_updates
ON books_silver.book_id = merge_key

WHEN MATCHED 
    AND books_silver.current = true 
    AND books_silver.price <> staged_updates.price 
THEN UPDATE SET 
    current = false, 
    end_date = staged_updates.updated

WHEN NOT MATCHED THEN 
INSERT (
    book_id, 
    title, 
    author, 
    price, 
    current, 
    effective_date, 
    end_date
)
VALUES (
    staged_updates.book_id, 
    staged_updates.title, 
    staged_updates.author, 
    staged_updates.price, 
    true, 
    staged_updates.updated, 
    NULL
);
