import { useMemo, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  MenuItem,
  TextField,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HomeWorkOutlinedIcon from '@mui/icons-material/HomeWorkOutlined';
import MeetingRoomOutlinedIcon from '@mui/icons-material/MeetingRoomOutlined';
import HotelOutlinedIcon from '@mui/icons-material/HotelOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/components/ui/PageHeader';
import { ModalForm } from '@/components/ui/ModalForm';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { formatCurrency } from '@/lib/format';
import { useAppDispatch, useAppSelector } from '@/hooks/useAppDispatch';
import { addBed, addFlat, addRoom, updateBed, updateFlat, updateRoom } from '@/app/slices/pgDataSlice';
import type { Bed, BedStatus, Flat, Room } from '@/types';

type ModalKind = 'flat' | 'room' | 'bed' | 'assign' | null;

interface FlatForm {
  name: string;
  address: string;
}

interface RoomForm {
  roomNumber: string;
}

interface BedForm {
  bedId: string;
  rentAmount: number;
  status: BedStatus;
}

function computeRoomStats(roomId: string, beds: Bed[]) {
  const roomBeds = beds.filter((b) => b.roomId === roomId);
  const occupied = roomBeds.filter((b) => b.status === 'occupied').length;
  return {
    totalBeds: roomBeds.length,
    occupiedBeds: occupied,
    vacantBeds: roomBeds.filter((b) => b.status === 'vacant').length,
  };
}

function computeFlatStats(flatId: string, rooms: Room[], beds: Bed[]) {
  const flatRooms = rooms.filter((r) => r.flatId === flatId);
  const flatBeds = beds.filter((b) => b.flatId === flatId);
  const occupied = flatBeds.filter((b) => b.status === 'occupied').length;
  return {
    totalRooms: flatRooms.length,
    totalBeds: flatBeds.length,
    occupiedBeds: occupied,
    vacantBeds: flatBeds.filter((b) => b.status === 'vacant').length,
  };
}

export function PropertiesPage() {
  const flats = useAppSelector((s) => s.pgData.flats);
  const rooms = useAppSelector((s) => s.pgData.rooms);
  const beds = useAppSelector((s) => s.pgData.beds);
  const tenants = useAppSelector((s) => s.pgData.tenants);
  const dispatch = useAppDispatch();

  const [modal, setModal] = useState<ModalKind>(null);
  const [contextFlatId, setContextFlatId] = useState<string | null>(null);
  const [contextRoomId, setContextRoomId] = useState<string | null>(null);
  const [editingFlat, setEditingFlat] = useState<Flat | null>(null);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [editingBed, setEditingBed] = useState<Bed | null>(null);
  const [assignBed, setAssignBed] = useState<Bed | null>(null);

  const flatForm = useForm<FlatForm>();
  const roomForm = useForm<RoomForm>();
  const bedForm = useForm<BedForm>();
  const assignForm = useForm<{ tenantId: string }>();

  const roomsByFlat = useMemo(() => {
    const map = new Map<string, Room[]>();
    for (const flat of flats) map.set(flat.id, []);
    for (const room of rooms) {
      const list = map.get(room.flatId) ?? [];
      list.push(room);
      map.set(room.flatId, list);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.roomNumber.localeCompare(b.roomNumber, undefined, { numeric: true }));
    }
    return map;
  }, [flats, rooms]);

  const bedsByRoom = useMemo(() => {
    const map = new Map<string, Bed[]>();
    for (const bed of beds) {
      const list = map.get(bed.roomId) ?? [];
      list.push(bed);
      map.set(bed.roomId, list);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.bedId.localeCompare(b.bedId, undefined, { numeric: true }));
    }
    return map;
  }, [beds]);

  const stats = useMemo(() => {
    const occupied = beds.filter((b) => b.status === 'occupied').length;
    return {
      properties: flats.length,
      rooms: rooms.length,
      beds: beds.length,
      vacant: beds.filter((b) => b.status === 'vacant').length,
      occupied,
    };
  }, [flats, rooms, beds]);

  const closeModal = () => {
    setModal(null);
    setEditingFlat(null);
    setEditingRoom(null);
    setEditingBed(null);
    setAssignBed(null);
    setContextFlatId(null);
    setContextRoomId(null);
  };

  const syncFlatWithData = (flatId: string, roomsData: Room[], bedsData: Bed[]) => {
    const flat = flats.find((f) => f.id === flatId);
    if (!flat) return;
    dispatch(updateFlat({ ...flat, ...computeFlatStats(flatId, roomsData, bedsData) }));
  };

  const syncRoomWithData = (roomId: string, bedsData: Bed[], roomsData: Room[]) => {
    const room = roomsData.find((r) => r.id === roomId);
    if (!room) return;
    dispatch(updateRoom({ ...room, ...computeRoomStats(roomId, bedsData) }));
    syncFlatWithData(room.flatId, roomsData, bedsData);
  };

  const openAddFlat = () => {
    setEditingFlat(null);
    flatForm.reset({ name: '', address: '' });
    setModal('flat');
  };

  const openEditFlat = (flat: Flat) => {
    setEditingFlat(flat);
    flatForm.reset({ name: flat.name, address: flat.address });
    setModal('flat');
  };

  const openAddRoom = (flatId: string) => {
    setContextFlatId(flatId);
    setEditingRoom(null);
    roomForm.reset({ roomNumber: '' });
    setModal('room');
  };

  const openEditRoom = (room: Room) => {
    setContextFlatId(room.flatId);
    setEditingRoom(room);
    roomForm.reset({ roomNumber: room.roomNumber });
    setModal('room');
  };

  const openAddBed = (flatId: string, room: Room) => {
    setContextFlatId(flatId);
    setContextRoomId(room.id);
    setEditingBed(null);
    const existing = bedsByRoom.get(room.id)?.length ?? 0;
    bedForm.reset({
      bedId: `${room.roomNumber}-B${existing + 1}`,
      rentAmount: 8500,
      status: 'vacant',
    });
    setModal('bed');
  };

  const openEditBed = (bed: Bed) => {
    setContextFlatId(bed.flatId);
    setContextRoomId(bed.roomId);
    setEditingBed(bed);
    bedForm.reset({ bedId: bed.bedId, rentAmount: bed.rentAmount, status: bed.status });
    setModal('bed');
  };

  const openAssign = (bed: Bed) => {
    setAssignBed(bed);
    assignForm.reset({ tenantId: '' });
    setModal('assign');
  };

  const onFlatSubmit = flatForm.handleSubmit((data) => {
    if (editingFlat) {
      dispatch(updateFlat({ ...editingFlat, ...data }));
    } else {
      const newFlat: Flat = {
        id: `f${Date.now()}`,
        ...data,
        totalRooms: 0,
        totalBeds: 0,
        occupiedBeds: 0,
        vacantBeds: 0,
      };
      dispatch(addFlat(newFlat));
    }
    closeModal();
  });

  const onRoomSubmit = roomForm.handleSubmit((data) => {
    const flatId = contextFlatId ?? editingRoom?.flatId;
    if (!flatId) return;
    const flat = flats.find((f) => f.id === flatId);

    if (editingRoom) {
      const updatedRoom: Room = {
        ...editingRoom,
        flatId,
        flatName: flat?.name ?? editingRoom.flatName,
        roomNumber: data.roomNumber,
        ...computeRoomStats(editingRoom.id, beds),
      };
      const updatedRooms = rooms.map((r) => (r.id === editingRoom.id ? updatedRoom : r));
      dispatch(updateRoom(updatedRoom));
      syncFlatWithData(flatId, updatedRooms, beds);
    } else {
      const newRoom: Room = {
        id: `r${Date.now()}`,
        flatId,
        flatName: flat?.name ?? '',
        roomNumber: data.roomNumber,
        totalBeds: 0,
        occupiedBeds: 0,
        vacantBeds: 0,
      };
      const updatedRooms = [...rooms, newRoom];
      dispatch(addRoom(newRoom));
      syncFlatWithData(flatId, updatedRooms, beds);
    }
    closeModal();
  });

  const onBedSubmit = bedForm.handleSubmit((data) => {
    const flatId = contextFlatId ?? editingBed?.flatId;
    const roomId = contextRoomId ?? editingBed?.roomId;
    if (!flatId || !roomId) return;
    const flat = flats.find((f) => f.id === flatId);
    const room = rooms.find((r) => r.id === roomId);

    if (editingBed) {
      const updatedBed: Bed = {
        ...editingBed,
        ...data,
        flatId,
        roomId,
        flatName: flat?.name ?? editingBed.flatName,
        roomNumber: room?.roomNumber ?? editingBed.roomNumber,
      };
      const updatedBeds = beds.map((b) => (b.id === editingBed.id ? updatedBed : b));
      dispatch(updateBed(updatedBed));
      syncRoomWithData(roomId, updatedBeds, rooms);
    } else {
      const newBed: Bed = {
        id: `b${Date.now()}`,
        ...data,
        flatId,
        roomId,
        flatName: flat?.name ?? '',
        roomNumber: room?.roomNumber ?? '',
      };
      const updatedBeds = [...beds, newBed];
      dispatch(addBed(newBed));
      syncRoomWithData(roomId, updatedBeds, rooms);
    }
    closeModal();
  });

  const onAssignSubmit = assignForm.handleSubmit(({ tenantId }) => {
    const tenant = tenants.find((t) => t.id === tenantId);
    if (assignBed && tenant) {
      const updatedBed: Bed = {
        ...assignBed,
        status: 'occupied',
        tenantId: tenant.id,
        tenantName: tenant.name,
      };
      const updatedBeds = beds.map((b) => (b.id === assignBed.id ? updatedBed : b));
      dispatch(updateBed(updatedBed));
      syncRoomWithData(assignBed.roomId, updatedBeds, rooms);
    }
    closeModal();
  });

  const contextFlat = contextFlatId ? flats.find((f) => f.id === contextFlatId) : null;
  const contextRoom = contextRoomId ? rooms.find((r) => r.id === contextRoomId) : null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Properties"
        description="Manage your buildings, rooms, and beds in one place — no mapping between screens."
        actions={
          <Button variant="contained" startIcon={<AddIcon />} onClick={openAddFlat}>
            Add property
          </Button>
        }
      />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Properties', value: stats.properties },
          { label: 'Rooms', value: stats.rooms },
          { label: 'Total beds', value: stats.beds },
          { label: 'Vacant beds', value: stats.vacant, highlight: true },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
          >
            <p className="text-sm text-slate-500">{item.label}</p>
            <p
              className={`text-2xl font-bold ${item.highlight ? 'text-amber-600' : 'text-slate-900 dark:text-white'}`}
            >
              {item.value}
            </p>
          </div>
        ))}
      </div>

      {flats.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center dark:border-slate-600 dark:bg-slate-800">
          <HomeWorkOutlinedIcon className="mb-3 text-4xl text-slate-400" />
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">No properties yet</h3>
          <p className="mt-1 text-sm text-slate-500">
            Start by adding a property (building). Then add rooms and beds inside it.
          </p>
          <Button variant="contained" startIcon={<AddIcon />} className="mt-4" onClick={openAddFlat}>
            Add your first property
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {flats.map((flat) => {
            const flatRooms = roomsByFlat.get(flat.id) ?? [];
            const flatBeds = beds.filter((b) => b.flatId === flat.id);
            const liveStats = computeFlatStats(flat.id, rooms, beds);

            return (
              <Accordion
                key={flat.id}
                defaultExpanded
                disableGutters
                className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card before:hidden dark:border-slate-700 dark:bg-slate-800"
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />} className="px-4 hover:bg-slate-50 dark:hover:bg-slate-800/80">
                  <div className="flex min-w-0 flex-1 items-center gap-3 pr-2">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600 dark:bg-brand-950">
                      <HomeWorkOutlinedIcon />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="truncate font-bold text-slate-900 dark:text-white">{flat.name}</p>
                      <p className="truncate text-sm text-slate-500">{flat.address}</p>
                      <p className="mt-0.5 text-xs text-slate-400">
                        {liveStats.totalRooms} rooms · {liveStats.totalBeds} beds · {liveStats.vacantBeds} vacant
                      </p>
                    </div>
                    <div className="hidden shrink-0 gap-1 sm:flex" onClick={(e) => e.stopPropagation()}>
                      <Button size="small" startIcon={<AddIcon />} onClick={() => openAddRoom(flat.id)}>
                        Add room
                      </Button>
                      <Button size="small" startIcon={<EditOutlinedIcon />} onClick={() => openEditFlat(flat)}>
                        Edit
                      </Button>
                    </div>
                  </div>
                </AccordionSummary>

                <AccordionDetails className="border-t border-slate-100 px-4 pb-4 pt-2 dark:border-slate-700">
                  <div className="mb-3 flex gap-2 sm:hidden">
                    <Button size="small" fullWidth variant="outlined" startIcon={<AddIcon />} onClick={() => openAddRoom(flat.id)}>
                      Add room
                    </Button>
                    <Button size="small" fullWidth variant="outlined" startIcon={<EditOutlinedIcon />} onClick={() => openEditFlat(flat)}>
                      Edit property
                    </Button>
                  </div>

                  {flatRooms.length === 0 ? (
                    <p className="rounded-lg bg-slate-50 py-6 text-center text-sm text-slate-500 dark:bg-slate-900">
                      No rooms in this property yet.{' '}
                      <button type="button" className="font-medium text-brand-600 hover:underline" onClick={() => openAddRoom(flat.id)}>
                        Add a room
                      </button>
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {flatRooms.map((room) => {
                        const roomBeds = bedsByRoom.get(room.id) ?? [];
                        const roomStats = computeRoomStats(room.id, beds);

                        return (
                          <div
                            key={room.id}
                            className="rounded-lg border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-600 dark:bg-slate-900/50"
                          >
                            <div className="flex flex-wrap items-start justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <MeetingRoomOutlinedIcon className="text-brand-600" fontSize="small" />
                                <div>
                                  <p className="font-semibold text-slate-900 dark:text-white">Room {room.roomNumber}</p>
                                  <p className="text-xs text-slate-500">
                                    {roomStats.totalBeds} beds · {roomStats.occupiedBeds} occupied · {roomStats.vacantBeds} vacant
                                  </p>
                                </div>
                              </div>
                              <div className="flex gap-1">
                                <Button size="small" startIcon={<AddIcon />} onClick={() => openAddBed(flat.id, room)}>
                                  Add bed
                                </Button>
                                <Button size="small" onClick={() => openEditRoom(room)}>
                                  Edit
                                </Button>
                              </div>
                            </div>

                            {roomBeds.length === 0 ? (
                              <p className="mt-3 text-sm text-slate-500">
                                No beds yet.{' '}
                                <button type="button" className="font-medium text-brand-600 hover:underline" onClick={() => openAddBed(flat.id, room)}>
                                  Add a bed
                                </button>
                              </p>
                            ) : (
                              <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                                {roomBeds.map((bed) => (
                                  <div
                                    key={bed.id}
                                    className="flex flex-col rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-600 dark:bg-slate-800"
                                  >
                                    <div className="flex items-start justify-between gap-2">
                                      <div className="flex items-center gap-2">
                                        <HotelOutlinedIcon fontSize="small" className="text-slate-400" />
                                        <span className="font-medium text-slate-900 dark:text-white">{bed.bedId}</span>
                                      </div>
                                      <StatusBadge status={bed.status} />
                                    </div>
                                    <p className="mt-1 text-sm text-slate-500">{formatCurrency(bed.rentAmount)} / month</p>
                                    {bed.tenantName && (
                                      <p className="mt-1 text-sm font-medium text-slate-700 dark:text-slate-300">{bed.tenantName}</p>
                                    )}
                                    <div className="mt-2 flex gap-1">
                                      <Button size="small" onClick={() => openEditBed(bed)}>
                                        Edit
                                      </Button>
                                      {bed.status === 'vacant' && (
                                        <Button size="small" startIcon={<PersonAddOutlinedIcon />} onClick={() => openAssign(bed)}>
                                          Assign
                                        </Button>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {flatBeds.length > 0 && (
                    <p className="mt-3 text-xs text-slate-400">
                      Est. revenue from occupied beds:{' '}
                      <span className="font-medium text-slate-600 dark:text-slate-300">
                        {formatCurrency(
                          flatBeds.filter((b) => b.status === 'occupied').reduce((sum, b) => sum + b.rentAmount, 0)
                        )}
                      </span>
                    </p>
                  )}
                </AccordionDetails>
              </Accordion>
            );
          })}
        </div>
      )}

      <ModalForm
        open={modal === 'flat'}
        title={editingFlat ? 'Edit property' : 'Add property'}
        onClose={closeModal}
        onSubmit={onFlatSubmit}
        submitLabel={editingFlat ? 'Update' : 'Create'}
      >
        <form className="flex flex-col gap-4 pt-2">
          <TextField label="Property name" placeholder="e.g. Sunshine PG" fullWidth {...flatForm.register('name', { required: true })} />
          <TextField label="Address" placeholder="Full address" fullWidth multiline rows={2} {...flatForm.register('address', { required: true })} />
          <p className="text-xs text-slate-500">After creating the property, add rooms and beds from the same screen.</p>
        </form>
      </ModalForm>

      <ModalForm
        open={modal === 'room'}
        title={editingRoom ? 'Edit room' : 'Add room'}
        onClose={closeModal}
        onSubmit={onRoomSubmit}
        submitLabel={editingRoom ? 'Update' : 'Create'}
      >
        <form className="flex flex-col gap-4 pt-2">
          {contextFlat && (
            <div className="rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-800 dark:bg-brand-950 dark:text-brand-200">
              Inside: <strong>{contextFlat.name}</strong>
            </div>
          )}
          <TextField label="Room number" placeholder="e.g. 101" fullWidth {...roomForm.register('roomNumber', { required: true })} />
          <p className="text-xs text-slate-500">
            {editingRoom ? 'Beds in this room are managed below.' : 'Add beds to this room after creating it.'}
          </p>
        </form>
      </ModalForm>

      <ModalForm
        open={modal === 'bed'}
        title={editingBed ? 'Edit bed' : 'Add bed'}
        onClose={closeModal}
        onSubmit={onBedSubmit}
        submitLabel={editingBed ? 'Update' : 'Create'}
      >
        <form className="flex flex-col gap-4 pt-2">
          {contextFlat && contextRoom && (
            <div className="rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-800 dark:bg-brand-950 dark:text-brand-200">
              Inside: <strong>{contextFlat.name}</strong> → Room <strong>{contextRoom.roomNumber}</strong>
            </div>
          )}
          <TextField label="Bed label" placeholder="e.g. 101-B1" fullWidth {...bedForm.register('bedId', { required: true })} />
          <TextField label="Monthly rent" type="number" fullWidth {...bedForm.register('rentAmount', { valueAsNumber: true })} />
          <TextField select label="Status" fullWidth defaultValue="vacant" {...bedForm.register('status')}>
            <MenuItem value="vacant">Vacant</MenuItem>
            <MenuItem value="occupied">Occupied</MenuItem>
            <MenuItem value="maintenance">Maintenance</MenuItem>
          </TextField>
        </form>
      </ModalForm>

      <ModalForm open={modal === 'assign'} title="Assign tenant to bed" onClose={closeModal} onSubmit={onAssignSubmit} submitLabel="Assign">
        <form className="flex flex-col gap-4 pt-2">
          {assignBed && (
            <div className="rounded-lg bg-slate-100 px-3 py-2 text-sm dark:bg-slate-800">
              Bed <strong>{assignBed.bedId}</strong> in {assignBed.flatName}, Room {assignBed.roomNumber}
            </div>
          )}
          <TextField select label="Select tenant" fullWidth {...assignForm.register('tenantId', { required: true })}>
            {tenants
              .filter((t) => !t.assignedBedId)
              .map((t) => (
                <MenuItem key={t.id} value={t.id}>
                  {t.name}
                </MenuItem>
              ))}
          </TextField>
        </form>
      </ModalForm>
    </div>
  );
}
