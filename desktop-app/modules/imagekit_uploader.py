#!/usr/bin/env python3
"""
ImageKit Uploader Module
Handles uploading images to ImageKit CDN.
"""

import os
import base64
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import requests
from requests.auth import HTTPBasicAuth


class ImageKitUploader:
    """
    Upload images to ImageKit CDN.
    
    Features:
    - Secure upload with authentication
    - Folder organization
    - Automatic retry on failure
    - URL generation
    - Bulk upload support
    """
    
    def __init__(self, config: dict):
        self.config = config
        ik_config = config.get("imagekit", {})
        
        # Check .env first, fallback to config.json
        self.public_key = os.getenv("IMAGEKIT_PUBLIC_KEY") or ik_config.get("public_key", "")
        self.private_key = os.getenv("IMAGEKIT_PRIVATE_KEY") or ik_config.get("private_key", "")
        self.url_endpoint = ik_config.get("url_endpoint", "")
        self.upload_folder = ik_config.get("upload_folder", "products")
        
        self.upload_url = "https://upload.imagekit.io/api/v1/files/upload"
        self.api_url = "https://api.imagekit.io/v1"
        
        # Retry settings
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def _get_auth(self) -> HTTPBasicAuth:
        """Get HTTP Basic Auth for ImageKit API."""
        return HTTPBasicAuth(self.private_key, "")
    
    def upload(
        self,
        file_path: str,
        folder: Optional[str] = None,
        filename: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload a single file to ImageKit.
        
        Args:
            file_path: Local path to the file
            folder: Remote folder path (e.g., "products/militaria/MILI-2025-0001")
            filename: Custom filename (optional, uses original if not provided)
            tags: List of tags to apply
            
        Returns:
            Dictionary with upload result including URL, or None on failure
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file and encode as base64
        with open(path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Build folder path
        remote_folder = f"/{self.upload_folder}"
        if folder:
            remote_folder = f"/{folder.strip('/')}"
        
        # Use original filename if not provided
        upload_filename = filename or path.name
        
        # Build request payload
        payload = {
            "file": file_data,
            "fileName": upload_filename,
            "folder": remote_folder,
            "useUniqueFileName": "false",
            "overwriteFile": "true"
        }
        
        if tags:
            payload["tags"] = ",".join(tags)
        
        # Upload with retry
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.upload_url,
                    data=payload,
                    auth=self._get_auth(),
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "fileId": result.get("fileId"),
                        "name": result.get("name"),
                        "url": result.get("url"),
                        "thumbnailUrl": result.get("thumbnailUrl"),
                        "filePath": result.get("filePath"),
                        "size": result.get("size"),
                        "width": result.get("width"),
                        "height": result.get("height")
                    }
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                last_error = str(e)
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (attempt + 1))
        
        print(f"Upload failed after {self.max_retries} attempts: {last_error}")
        return None
    
    def upload_batch(
        self,
        file_paths: List[str],
        folder: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Upload multiple files to ImageKit.
        
        Args:
            file_paths: List of local file paths
            folder: Remote folder for all files
            progress_callback: Optional callback(current, total, filename)
            
        Returns:
            Dictionary with batch results
        """
        results = {
            "total": len(file_paths),
            "uploaded": 0,
            "failed": 0,
            "files": [],
            "errors": []
        }
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i + 1, len(file_paths), Path(file_path).name)
            
            try:
                result = self.upload(file_path, folder)
                
                if result and result.get("success"):
                    results["uploaded"] += 1
                    results["files"].append(result)
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "file": file_path,
                        "error": "Upload returned no result"
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return results
    
    def get_file_details(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of an uploaded file.
        
        Args:
            file_id: ImageKit file ID
            
        Returns:
            File details dictionary
        """
        try:
            response = requests.get(
                f"{self.api_url}/files/{file_id}/details",
                auth=self._get_auth(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting file details: {e}")
        
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from ImageKit.
        
        Args:
            file_id: ImageKit file ID
            
        Returns:
            True if deleted successfully
        """
        try:
            response = requests.delete(
                f"{self.api_url}/files/{file_id}",
                auth=self._get_auth(),
                timeout=30
            )
            
            return response.status_code == 204
            
        except requests.exceptions.RequestException as e:
            print(f"Error deleting file: {e}")
            return False
    
    def list_files(
        self,
        folder: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List files in ImageKit.
        
        Args:
            folder: Folder path to list
            limit: Maximum number of files to return
            
        Returns:
            List of file objects
        """
        try:
            params = {"limit": limit}
            if folder:
                params["path"] = folder
            
            response = requests.get(
                f"{self.api_url}/files",
                params=params,
                auth=self._get_auth(),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            print(f"Error listing files: {e}")
        
        return []
    
    def create_folder(self, folder_path: str) -> bool:
        """
        Create a folder in ImageKit.
        
        Args:
            folder_path: Path for the new folder
            
        Returns:
            True if created successfully
        """
        try:
            response = requests.post(
                f"{self.api_url}/folder",
                json={"folderName": folder_path.split("/")[-1], "parentFolderPath": "/".join(folder_path.split("/")[:-1]) or "/"},
                auth=self._get_auth(),
                timeout=30
            )
            
            return response.status_code in (200, 201)
            
        except requests.exceptions.RequestException as e:
            print(f"Error creating folder: {e}")
            return False
    
    def get_url_with_transforms(
        self,
        file_path: str,
        transforms: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a URL with ImageKit transformations.
        
        Args:
            file_path: Path to the file on ImageKit
            transforms: Dictionary of transformation parameters
            
        Returns:
            Transformed URL
        """
        base_url = self.url_endpoint.rstrip("/")
        
        if not transforms:
            return f"{base_url}/{file_path.lstrip('/')}"
        
        # Build transformation string
        transform_parts = []
        for key, value in transforms.items():
            transform_parts.append(f"{key}-{value}")
        
        transform_str = ",".join(transform_parts)
        
        return f"{base_url}/tr:{transform_str}/{file_path.lstrip('/')}"
    
    def generate_product_urls(
        self,
        uploaded_files: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Generate standard product image URLs with thumbnails.
        
        Args:
            uploaded_files: List of upload results
            
        Returns:
            List of URL sets for each image
        """
        url_sets = []
        
        for file_info in uploaded_files:
            file_path = file_info.get("filePath", "")
            
            url_set = {
                "original": file_info.get("url"),
                "large": self.get_url_with_transforms(file_path, {"w": "1200", "q": "90"}),
                "medium": self.get_url_with_transforms(file_path, {"w": "800", "q": "85"}),
                "thumbnail": self.get_url_with_transforms(file_path, {"w": "400", "h": "400", "c": "at_max", "q": "80"}),
                "square": self.get_url_with_transforms(file_path, {"w": "600", "h": "600", "c": "maintain_ratio", "q": "85"})
            }
            
            url_sets.append(url_set)
        
        return url_sets
