"use client";

import { Calendar, MapPin, Users, DollarSign } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { NexusEvent, EventStatus } from "@/lib/mock-data";

interface EventCardProps {
  event: NexusEvent;
  onClick?: () => void;
}

const STATUS_CONFIG: Record<EventStatus, { label: string; className: string }> = {
  upcoming: {
    label: "Upcoming",
    className: "bg-blue-100 text-blue-800 hover:bg-blue-100",
  },
  "in-progress": {
    label: "In Progress",
    className: "bg-green-100 text-green-800 hover:bg-green-100",
  },
  completed: {
    label: "Completed",
    className: "bg-slate-100 text-slate-800 hover:bg-slate-100",
  },
  planning: {
    label: "Planning",
    className: "bg-amber-100 text-amber-800 hover:bg-amber-100",
  },
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDateRange(start: string, end?: string): string {
  if (!end) return formatDate(start);

  const startDate = new Date(start);
  const endDate = new Date(end);

  // Same month and year
  if (
    startDate.getMonth() === endDate.getMonth() &&
    startDate.getFullYear() === endDate.getFullYear()
  ) {
    return `${startDate.toLocaleDateString("en-US", { month: "short", day: "numeric" })} - ${endDate.getDate()}, ${endDate.getFullYear()}`;
  }

  return `${formatDate(start)} - ${formatDate(end)}`;
}

export function EventCard({ event, onClick }: EventCardProps) {
  const statusConfig = STATUS_CONFIG[event.status];
  const budgetProgress = event.budget && event.budgetUsed
    ? (event.budgetUsed / event.budget) * 100
    : 0;

  return (
    <Card
      className={cn(
        "transition-all hover:shadow-md",
        onClick && "cursor-pointer hover:border-primary/50"
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1">
            <CardTitle className="text-lg">{event.name}</CardTitle>
            <CardDescription className="line-clamp-2">
              {event.description}
            </CardDescription>
          </div>
          <Badge variant="secondary" className={cn("shrink-0", statusConfig.className)}>
            {statusConfig.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Event Details */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>{formatDateRange(event.date, event.endDate)}</span>
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <MapPin className="h-4 w-4" />
            <span className="truncate">{event.location}</span>
          </div>
          {event.attendees && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>{event.attendees} attendees</span>
            </div>
          )}
          {event.budget && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <DollarSign className="h-4 w-4" />
              <span>${event.budget.toLocaleString()} budget</span>
            </div>
          )}
        </div>

        {/* Budget Progress */}
        {event.budget && event.budgetUsed !== undefined && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Budget Used</span>
              <span className="font-medium">
                ${event.budgetUsed.toLocaleString()} / ${event.budget.toLocaleString()}
              </span>
            </div>
            <Progress value={budgetProgress} className="h-2" />
          </div>
        )}

        {/* Teams */}
        <div className="flex flex-wrap gap-1.5">
          {event.teams.map((team) => (
            <Badge key={team} variant="outline" className="text-xs capitalize">
              {team}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
