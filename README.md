# Base Microservice

This is a template for a basic microservice.

Feel free to add to and edit as required.

## Thoughts

- It did not take me long to understand the code structure, however I did find difficulties in running it locally
  without docker compose as I wanted to understand execution of all the services. I was managed to run the services
  individually on local machine without docker compose
- It took me 10-12 async hours to approach the problem and implement the all prioritized tasks.
- I have also included files table schema for your reference
- I have written [future improvements](#future-improvements) which comes to my mind while I was approaching to the
  problem
- I have implemented all the requirements including the retrieval of static images which works when we have shared
  storage volume (scratch)
- I also found an issue while running worker on docker compose. Actually, the worker starts but won't wait for the db
  and rabbitmq to be in ready state even if we add depends_on. So I modify the bash command which is same in web
  container

## DB Schema

Files Table

- id (`pk`) (UUID)
- name
- type (png, pdf, jpg, jpeg)
- path (s3 or local storage)
- output_path (s3, or local storage)
- resolution
- output_resolution
- status (uploading, uploaded, processing, completed, failure)
- page_num
- pdf_id (`fk`)

## Endpoints

`files`

- `GET /api/files/{file_id}`
    - returns files data based on id
- `POST /api/files/upload`
    - Upload files and returns id
    - Allowed extensions _png_, _jpg_, _pdf_, _jpeg_
- `POST /api/files/{file_id}/paths`
    - Returns files input/output paths along with resolution
- `GET /api/files/{file_id}/status`
    - Returns status of files
- `GET /static/{file_name}`
    - Returns file object
    - Folder name : `scratch`

## Use Cases

`files`

- get_file_by_id()
    - Returns file details
- get_file_status_by_id()
    - Returns file status
- upload()
    - upload_pdf_file()
        - Store file details in db
        - Invoke celery tasks upload_file() and convert_to_png()
    - upload_image_file()
        - Store file details in db
        - Invoke celery tasks upload_file() and convert_to_png()
- get_file_paths_by_id()
    - Returns file paths, resolution details

`Celery tasks`

- upload_file()
    - Save file to local storage (`/scratch`)
    - Update records of file such as status, path, etc
- convert_to_png()
    - Convert the input file into png with specified resolution (3500x3500)
    - Update records of file such as status, resolution, etc.

## Future Improvements

- Use of websockets to check real-time status of file processing
- S3 bucket for storing images
- CDN bucket for retrieving images quickly
- Add unit tests to ensure the use cases is working correctly.
    - We can use mock objects for database operations
- Add error handling for invalid inputs
    - Filenames with `../../file.pdf`
    - png file containing jpg data
- Implement users management for managing respective files of the users since anyone has access to files data with
  unique id
    - Implement relationship between *files* and *users* table
    - JWT token for authentication and authorization of apis
- Allow only certain amount of images to be uploaded (max 10 images)
    - If user is uploading pdf then total count of images should be not exceed max count
- Allow limited size of images (max 5 MB)

---

## What's included

- FastAPI (examples in `src/app/main.py`)
- Celery (examples in `src/app/workers/tasks.py`)
- SQLAlchemy (models in `src/app/models.py`)
- Alembic (migrations in `src/app/migrations/versions`)
- PostgreSQL
- RabbitMQ
- autoreload on code changes (works on most architectures)
- Imagemagick with PDF support (Ghostscript)
- [Wand library](https://docs.wand-py.org/) for Imagemagick

## Getting started

0) Install Docker
1) Clone the repository
2) Use `docker-compose up` in your Terminal to start the Docker container.
3) The app is defaulted to run on `localhost:8000`
    * `/`: The root url (contents from `src/main.py`)
    * `/health`: URL endpoint for a basic healthcheck. Displays alembic version and Celery worker ping responses. <br>
      Example of healthy response:
    ```json
    {
      "alembic_version":"c4f1de9fd1e1",
      "celery_response":[{"celery@fada80fe0ab9":{"ok":"pong"}}]
    }
    ```
    * `/test-task`: Runs a basic async Celery task.

## Migrating database

- `docker-compose stop`
- `docker-compose up`

## Rebuild infrastructure (not for code changes)

- `docker-compose build`

## Troubleshooting

- `docker-compose down` (This will destroy all your containers for the project)
- `docker-compose up`
