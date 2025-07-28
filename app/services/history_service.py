from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from supabase import Client
from app.config.supabase import get_supabase_client
from app.models.requests import (
    CommandHistoryResponse,
    CommandHistoryListResponse,
    CommandStatsResponse
)

class HistoryService:
    def __init__(self):
        self.supabase: Client = get_supabase_client()

    async def log_command(
        self,
        user_id: UUID,
        command: str,
        input_text: str,
        output_text: Optional[str] = None,
        agent_used: Optional[str] = None,
        success: bool = True,
        processing_time_ms: Optional[int] = None
    ) -> CommandHistoryResponse:
        """Log a command execution."""
        try:
            command_data = {
                "user_id": str(user_id),
                "command": command,
                "input_text": input_text,
                "output_text": output_text,
                "agent_used": agent_used,
                "success": success,
                "processing_time_ms": processing_time_ms
            }
            
            result = self.supabase.table("command_history") \
                .insert(command_data) \
                .execute()
            
            if not result.data:
                raise Exception("Failed to log command")
            
            return CommandHistoryResponse(**result.data[0])
            
        except Exception as e:
            raise Exception(f"Failed to log command: {str(e)}")

    async def get_command_history(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
        command_filter: Optional[str] = None,
        success_filter: Optional[bool] = None,
        days_back: Optional[int] = None
    ) -> CommandHistoryListResponse:
        """Get user's command history with filtering."""
        try:
            # Start building the query
            query = self.supabase.table("command_history") \
                .select("*") \
                .eq("user_id", str(user_id))
            
            # Apply filters
            if command_filter:
                query = query.ilike("command", f"%{command_filter}%")
            
            if success_filter is not None:
                query = query.eq("success", success_filter)
            
            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                query = query.gte("created_at", cutoff_date.isoformat())
            
            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Apply pagination and ordering
            offset = (page - 1) * per_page
            result = query \
                .order("created_at", desc=True) \
                .range(offset, offset + per_page - 1) \
                .execute()
            
            commands = [CommandHistoryResponse(**cmd) for cmd in result.data]
            pages = (total + per_page - 1) // per_page
            
            return CommandHistoryListResponse(
                commands=commands,
                total=total,
                page=page,
                per_page=per_page,
                pages=pages
            )
            
        except Exception as e:
            raise Exception(f"Failed to get command history: {str(e)}")

    async def get_command_stats(
        self,
        user_id: UUID,
        days_back: int = 30
    ) -> CommandStatsResponse:
        """Get command usage statistics."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Get all commands in the time range
            result = self.supabase.table("command_history") \
                .select("command, success, processing_time_ms") \
                .eq("user_id", str(user_id)) \
                .gte("created_at", cutoff_date.isoformat()) \
                .execute()
            
            if not result.data:
                return CommandStatsResponse(
                    total_commands=0,
                    success_rate=0.0,
                    most_used_commands=[],
                    avg_processing_time=None
                )
            
            commands = result.data
            total_commands = len(commands)
            successful_commands = sum(1 for cmd in commands if cmd["success"])
            success_rate = successful_commands / total_commands if total_commands > 0 else 0.0
            
            # Calculate most used commands
            command_counts = {}
            processing_times = []
            
            for cmd in commands:
                command_name = cmd["command"]
                command_counts[command_name] = command_counts.get(command_name, 0) + 1
                
                if cmd["processing_time_ms"]:
                    processing_times.append(cmd["processing_time_ms"])
            
            # Sort commands by usage
            most_used_commands = [
                {"command": cmd, "count": count, "percentage": round((count / total_commands) * 100, 1)}
                for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Calculate average processing time
            avg_processing_time = None
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
            
            return CommandStatsResponse(
                total_commands=total_commands,
                success_rate=round(success_rate, 3),
                most_used_commands=most_used_commands,
                avg_processing_time=avg_processing_time
            )
            
        except Exception as e:
            raise Exception(f"Failed to get command stats: {str(e)}")

    async def search_commands(
        self,
        user_id: UUID,
        search_term: str,
        search_in: str = "both"  # "command", "input", "output", "both"
    ) -> List[CommandHistoryResponse]:
        """Search through command history."""
        try:
            query = self.supabase.table("command_history") \
                .select("*") \
                .eq("user_id", str(user_id))
            
            if search_in == "command":
                query = query.ilike("command", f"%{search_term}%")
            elif search_in == "input":
                query = query.ilike("input_text", f"%{search_term}%")
            elif search_in == "output":
                query = query.ilike("output_text", f"%{search_term}%")
            else:  # both or any other value
                # Use OR logic for multiple fields (requires raw SQL or multiple queries)
                # For simplicity, we'll search in command and input_text
                cmd_result = self.supabase.table("command_history") \
                    .select("*") \
                    .eq("user_id", str(user_id)) \
                    .ilike("command", f"%{search_term}%") \
                    .execute()
                
                input_result = self.supabase.table("command_history") \
                    .select("*") \
                    .eq("user_id", str(user_id)) \
                    .ilike("input_text", f"%{search_term}%") \
                    .execute()
                
                # Combine and deduplicate results
                combined_data = {}
                for cmd in (cmd_result.data or []):
                    combined_data[cmd["id"]] = cmd
                for cmd in (input_result.data or []):
                    combined_data[cmd["id"]] = cmd
                
                commands = [CommandHistoryResponse(**cmd) for cmd in combined_data.values()]
                return sorted(commands, key=lambda x: x.created_at, reverse=True)
            
            result = query.order("created_at", desc=True).limit(100).execute()
            return [CommandHistoryResponse(**cmd) for cmd in result.data]
            
        except Exception as e:
            raise Exception(f"Failed to search commands: {str(e)}")

    async def delete_old_history(
        self,
        user_id: UUID,
        days_to_keep: int = 90
    ) -> int:
        """Delete old command history entries."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            result = self.supabase.table("command_history") \
                .delete() \
                .eq("user_id", str(user_id)) \
                .lt("created_at", cutoff_date.isoformat()) \
                .execute()
            
            return len(result.data) if result.data else 0
            
        except Exception as e:
            raise Exception(f"Failed to delete old history: {str(e)}")

    async def get_popular_commands(
        self,
        user_id: UUID,
        limit: int = 10,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get most popular commands for suggestions."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            result = self.supabase.table("command_history") \
                .select("command") \
                .eq("user_id", str(user_id)) \
                .eq("success", True) \
                .gte("created_at", cutoff_date.isoformat()) \
                .execute()
            
            if not result.data:
                return []
            
            # Count command frequency
            command_counts = {}
            for cmd in result.data:
                command = cmd["command"]
                command_counts[command] = command_counts.get(command, 0) + 1
            
            # Sort and return top commands
            popular_commands = [
                {"command": cmd, "count": count}
                for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
            ]
            
            return popular_commands
            
        except Exception as e:
            raise Exception(f"Failed to get popular commands: {str(e)}")