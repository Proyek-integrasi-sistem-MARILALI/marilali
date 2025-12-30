"""
POI Enrichment Service - Merges OpenDataBay and OpenStreetMap data.
Implements the data integration logic with fuzzy matching and provenance tracking.
"""

import asyncio
from typing import List, Dict, Optional
from difflib import SequenceMatcher

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.destination.models import Destination
from src.map.openstreetmap_service import osm_service
from src.destination.opendatabay_importer import opendatabay_importer


class POIEnrichmentService:
    def __init__(self):
        self.match_threshold = 0.65  # Minimum 65% combined score for match
        self.max_distance_km = 0.5   # Maximum 500m distance for match
    
    async def enrich_all_destinations(self, db: AsyncSession) -> Dict[str, int]:
        print(" Starting POI enrichment process for Bali...")
        
        # Step 1: Import OpenDataBay data
        print("\n Step 1: Importing OpenDataBay destinations...")
        opendatabay_count = await opendatabay_importer.import_to_database(db)
        
        # Step 2: Fetch OSM POIs
        print("\n Step 2: Fetching OpenStreetMap POIs...")
        osm_pois = await osm_service.get_all_bali_pois()
        all_osm_pois = []
        for category, pois in osm_pois.items():
            all_osm_pois.extend(pois)
        
        print(f" Fetched {len(all_osm_pois)} POIs from OpenStreetMap")
        
        # Step 3: Match and enrich
        print("\n Step 3: Matching and enriching destinations...")
        enrichment_stats = await self._match_and_enrich(db, all_osm_pois)
        
        # Step 4: Import unmatched OSM POIs
        print("\n Step 4: Importing unmatched OSM POIs...")
        osm_only_count = await self._import_unmatched_osm_pois(db, all_osm_pois)
        
        stats = {
            "opendatabay": opendatabay_count,
            "merged": enrichment_stats["enriched"],
            "osm_only": osm_only_count,
            "total": opendatabay_count + osm_only_count
        }
        
        print("\n" + "="*60)
        print("POI Enrichment Complete!")
        print(f"    OpenDataBay destinations: {stats['opendatabay']}")
        print(f"    Enriched with OSM data: {stats['merged']}")
        print(f"    OSM-only POIs added: {stats['osm_only']}")
        print(f"    Total destinations: {stats['total']}")
        print("="*60)
        
        return stats
    
    async def _match_and_enrich(
        self,
        db: AsyncSession,
        osm_pois: List[Dict]
    ) -> Dict[str, int]:
        # Get all OpenDataBay destinations
        result = await db.execute(
            select(Destination).where(
                Destination.source.in_(["opendatabay", "manual"])
            )
        )
        opendatabay_dests = result.scalars().all()
        
        enriched_count = 0
        matched_osm_ids = set()
        
        for dest in opendatabay_dests:
            # Skip if already enriched
            if dest.source == "opendatabay+openstreetmap":
                continue
            
            # Skip if no coordinates
            if not dest.latitude or not dest.longitude:
                continue
            
            # Find best OSM match
            osm_match = osm_service.find_nearby_match(
                name=dest.name,
                lat=dest.latitude,
                lon=dest.longitude,
                pois=osm_pois,
                max_distance_km=self.max_distance_km
            )
            
            if osm_match:
                # Enrich destination with OSM data
                dest.source = "opendatabay+openstreetmap"
                dest.osm_id = str(osm_match["osm_id"])
                dest.osm_type = osm_match["osm_type"]
                dest.osm_tags = osm_match["tags"]
                
                # Update fields if better data available
                if not dest.website and osm_match.get("website"):
                    dest.website = osm_match["website"]
                if not dest.contact_info and osm_match.get("phone"):
                    dest.contact_info = osm_match["phone"]
                if not dest.address and osm_match.get("address"):
                    dest.address = osm_match["address"]
                
                enriched_count += 1
                matched_osm_ids.add(osm_match["osm_id"])
                
                if enriched_count % 10 == 0:
                    print(f"  Enriched {enriched_count} destinations...")
        
        await db.commit()
        
        # Store matched IDs for later filtering
        self._matched_osm_ids = matched_osm_ids
        
        print(f" Enriched {enriched_count} destinations with OSM data")
        
        return {"enriched": enriched_count}
    
    async def _import_unmatched_osm_pois(
        self,
        db: AsyncSession,
        osm_pois: List[Dict]
    ) -> int:
        matched_ids = getattr(self, '_matched_osm_ids', set())
        imported_count = 0
        
        for poi in osm_pois:
            # Skip if already matched
            if poi["osm_id"] in matched_ids:
                continue
            
            # Check if already exists
            existing = await db.execute(
                select(Destination).where(
                    Destination.osm_id == str(poi["osm_id"])
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            # Create new destination from OSM data
            destination = Destination(
                name=poi["name"],
                description=self._generate_description_from_tags(poi["tags"]),
                category=self._map_osm_category(poi),
                location=poi.get("address") or "Bali, Indonesia",
                city="Bali",
                country="Indonesia",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                address=poi.get("address"),
                website=poi.get("website"),
                contact_info=poi.get("phone"),
                source="openstreetmap",
                osm_id=str(poi["osm_id"]),
                osm_type=poi["osm_type"],
                osm_tags=poi["tags"]
            )
            
            db.add(destination)
            imported_count += 1
            
            if imported_count % 20 == 0:
                await db.commit()
                print(f"Imported {imported_count} OSM POIs...")
        
        await db.commit()
        
        print(f"Imported {imported_count} new POIs from OpenStreetMap")
        
        return imported_count
    
    def _map_osm_category(self, poi: Dict) -> str:
        """Map OSM tags to application categories."""
        tags = poi.get("tags", {})
        
        # Priority mapping
        if poi.get("tourism_type"):
            tourism_map = {
                "attraction": "attraction",
                "hotel": "accommodation",
                "hostel": "accommodation",
                "guest_house": "accommodation",
                "museum": "cultural",
                "viewpoint": "nature",
                "theme_park": "entertainment"
            }
            return tourism_map.get(poi["tourism_type"], "attraction")
        
        if poi.get("natural_type") == "beach":
            return "beach"
        
        if poi.get("amenity_type") == "place_of_worship":
            return "cultural"
        
        if poi.get("amenity_type") in ["restaurant", "cafe", "bar"]:
            return "food"
        
        return "other"
    
    def _generate_description_from_tags(self, tags: Dict) -> str:
        """Generate a basic description from OSM tags."""
        desc_parts = []
        
        if tags.get("description"):
            return tags["description"]
        
        if tags.get("tourism"):
            desc_parts.append(f"A {tags['tourism']} in Bali")
        
        if tags.get("amenity"):
            desc_parts.append(f"Features: {tags['amenity']}")
        
        if tags.get("cuisine"):
            desc_parts.append(f"Cuisine: {tags['cuisine']}")
        
        return ". ".join(desc_parts) if desc_parts else "Located in Bali, Indonesia"


# Singleton instance
poi_enrichment_service = POIEnrichmentService()


# CLI helper
async def run_enrichment():
    """Run the enrichment from command line."""
    from src.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        stats = await poi_enrichment_service.enrich_all_destinations(db)
        print(f"\nEnrichment complete! Stats: {stats}")


if __name__ == "__main__":
    asyncio.run(run_enrichment())
