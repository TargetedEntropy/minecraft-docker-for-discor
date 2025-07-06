"""
Modpack utility functions for handling modpack URLs and validation
"""

import aiohttp
import asyncio
import logging
from pathlib import Path
from typing import Optional
import tempfile
import zipfile

logger = logging.getLogger(__name__)


class ModpackHelper:
    """Helper class for modpack operations"""
    
    @staticmethod
    async def validate_modpack_url(url: str) -> bool:
        """Validate that a modpack URL is accessible and is a zip file"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=10) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '').lower()
                        content_disposition = response.headers.get('content-disposition', '').lower()
                        
                        # Check if it's a zip file by content type or filename
                        is_zip = (
                            'application/zip' in content_type or
                            'application/x-zip' in content_type or
                            '.zip' in content_disposition or
                            url.lower().endswith('.zip')
                        )
                        
                        return is_zip
                    return False
        except Exception as e:
            logger.error(f"Error validating modpack URL {url}: {e}")
            return False
    
    @staticmethod
    async def get_modpack_info(url: str) -> Optional[dict]:
        """Get basic information about a modpack from its URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url, timeout=10) as response:
                    if response.status == 200:
                        content_length = response.headers.get('content-length')
                        last_modified = response.headers.get('last-modified')
                        
                        # Extract filename from URL or content-disposition
                        filename = url.split('/')[-1]
                        content_disposition = response.headers.get('content-disposition', '')
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"\'')
                        
                        return {
                            'filename': filename,
                            'size': int(content_length) if content_length else None,
                            'last_modified': last_modified,
                            'url': url
                        }
        except Exception as e:
            logger.error(f"Error getting modpack info for {url}: {e}")
        
        return None
    
    @staticmethod
    def extract_modpack_metadata(zip_path: str) -> dict:
        """Extract metadata from a modpack zip file"""
        metadata = {
            'minecraft_version': None,
            'mod_loader': None,
            'mod_count': 0,
            'has_config': False
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                
                # Count mod files
                mod_files = [f for f in file_list if f.endswith('.jar') and ('mods/' in f or 'mods\\' in f)]
                metadata['mod_count'] = len(mod_files)
                
                # Check for config directory
                config_files = [f for f in file_list if 'config/' in f or 'config\\' in f]
                metadata['has_config'] = len(config_files) > 0
                
                # Try to detect mod loader type
                if any('forge' in f.lower() for f in file_list):
                    metadata['mod_loader'] = 'forge'
                elif any('fabric' in f.lower() for f in file_list):
                    metadata['mod_loader'] = 'fabric'
                elif any('neoforge' in f.lower() for f in file_list):
                    metadata['mod_loader'] = 'neoforge'
                elif any('quilt' in f.lower() for f in file_list):
                    metadata['mod_loader'] = 'quilt'
                
                # Try to find version info from manifest or other files
                for file_name in file_list:
                    if 'manifest.json' in file_name.lower():
                        try:
                            manifest_content = zip_file.read(file_name).decode('utf-8')
                            import json
                            manifest = json.loads(manifest_content)
                            if 'minecraft' in manifest:
                                metadata['minecraft_version'] = manifest['minecraft'].get('version')
                            if 'modLoaders' in manifest and manifest['modLoaders']:
                                loader_info = manifest['modLoaders'][0]
                                metadata['mod_loader'] = loader_info.get('id', '').split('-')[0]
                        except Exception:
                            pass
                        break
                
        except Exception as e:
            logger.error(f"Error extracting modpack metadata from {zip_path}: {e}")
        
        return metadata
