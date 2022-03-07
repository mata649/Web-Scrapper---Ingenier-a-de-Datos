from asyncio.log import logger
import logging
import argparse
from urllib.parse import urlparse
import pandas as pd
import hashlib

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def _read_data(filename: str):
    logger.info(f'Reading {filename}')
    df = pd.read_csv(f'./DB/{filename}')
    return df


def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('-')[0]
    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'Filling newspaper_uid column with {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid
    return df


def _extract_host(df):
    logger.info("Extracting host")
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df


def _cleaning_nan_autors(df: pd.DataFrame):
    df['autor'] = df['autor'].fillna('Unknown')
    return df


def _adding_uids(df: pd.DataFrame):
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest()))
    df['uid'] = uids
    df.set_index('uid', inplace=True)
    return df


def transform(filename: str):
    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _cleaning_nan_autors(df)
    df = _adding_uids(df)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', help='The path to the dirty data', type=str)
    arg = parser.parse_args()
    df = transform(arg.filename)
    print(df)
