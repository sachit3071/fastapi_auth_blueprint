import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, Table, Column, String, TIMESTAMP
from alembic import context
from dotenv import load_dotenv
from pathlib import Path
from alembic.script import ScriptDirectory
from sqlalchemy.sql import func
import sys
from models.models import Base
from config.database import DatabaseConfig as Config

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


load_dotenv()

ERP_DB_SCHEMA_NAME = Config.from_env().erp_db_schema_name
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# here we allow ourselves to pass interpolation vars to alembic.ini from the host env
section = config.config_ini_section
config.set_section_option(section, "DB_HOST", str(os.environ.get("DB_HOST")))
config.set_section_option(section, "DB_PORT", str(os.environ.get("DB_PORT")))
config.set_section_option(section, "DB_USER", str(os.environ.get("DB_USER")))
config.set_section_option(section, "DB_PASSWORD", str(os.environ.get("DB_PASSWORD")))
config.set_section_option(section, "DB_NAME", str(os.environ.get("DB_NAME")))


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
target_metadata.schema = ERP_DB_SCHEMA_NAME

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_next_number(versions_path):
    existing_files = list(Path(versions_path).glob("*.py"))
    if not existing_files:
        return 1
    return (
        max(
            int(file.stem.split("_")[0])
            for file in existing_files
            if file.stem[0].isdigit()
        )
        + 1
    )


def generate_migration_prefix(config, *args, **kwargs):
    script = ScriptDirectory.from_config(config)
    versions_path = script.versions
    next_number = get_next_number(versions_path)
    return f"{next_number:03d}"


alembic_version = Table(
    "alembic_version",
    Base.metadata,
    Column("version_num", String(32), primary_key=True),
    Column("applied_at", TIMESTAMP, server_default=func.now(), nullable=False),
    Column("model_name", String(255), server_default="unknown", nullable=False),
    schema=ERP_DB_SCHEMA_NAME,
)


def process_revision_directives(context, revision, directives):
    """Process revision directives to add custom logic."""
    if directives and hasattr(directives[0], "message"):
        # This is a new revision
        message = directives[0].message
    else:
        message = ""

    # Generate new revision id
    script = ScriptDirectory.from_config(context.config)
    prefix = generate_migration_prefix(context.config)
    old_revision_id = directives[0].rev_id if directives else None
    new_revision_id = f"{prefix}_{old_revision_id}"

    # Update the revision ID and construct the new filename
    if directives:
        directives[0].rev_id = new_revision_id
        new_filename = (
            f"{new_revision_id}_{message}.py" if message else f"{new_revision_id}.py"
        )
        directives[0].path = os.path.join(script.versions, new_filename)

    return directives


def include_object(object, name, type_, reflected, compare_to):
    """Include or exclude objects from migration scripts."""
    if type_ == "table":
        return object.schema == ERP_DB_SCHEMA_NAME
    if (type_ == "table" and object.schema == ERP_DB_SCHEMA_NAME) or (
        type_ == "table"
        and object.schema == ERP_DB_SCHEMA_NAME
        and name == "alembic_version"
    ):
        return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
        include_schemas=True,
        version_table_schema=ERP_DB_SCHEMA_NAME,
        include_object=include_object,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.execute(f"CREATE SCHEMA IF NOT EXISTS {ERP_DB_SCHEMA_NAME};")
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_schemas=True,
            version_table_schema=ERP_DB_SCHEMA_NAME,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.execute(f"CREATE SCHEMA IF NOT EXISTS {ERP_DB_SCHEMA_NAME};")
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
