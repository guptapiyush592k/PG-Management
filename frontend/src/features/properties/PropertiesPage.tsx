import { useMemo, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  MenuItem,
  TextField,
  Typography,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HomeWorkOutlinedIcon from '@mui/icons-material/HomeWorkOutlined';
import MeetingRoomOutlinedIcon from '@mui/icons-material/MeetingRoomOutlined';
import HotelOutlinedIcon from '@mui/icons-material/HotelOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import { useForm } from 'react-hook-form';
import { PageHeader } from '@/shared/components/ui/PageHeader';
import { ModalForm } from '@/shared/components/ui/ModalForm';
import { StatusBadge } from '@/shared/components/ui/StatusBadge';
import { SkeletonLoader } from '@/shared/components/ui/SkeletonLoader';
import { EmptyState } from '@/shared/components/ui/EmptyState';
import { formatCurrency, getApiErrorMessage } from '@/shared/utils/format';
import { useFlatsQuery, useCreateFlatMutation, useUpdateFlatMutation } from '@/shared/hooks/queries/useFlats';
import { useRoomsQuery, useCreateRoomMutation, useUpdateRoomMutation } from '@/shared/hooks/queries/useRooms';
import { useBedsQuery, useCreateBedMutation, useUpdateBedMutation } from '@/shared/hooks/queries/useBeds';
import { useResidentsQuery } from '@/shared/hooks/queries/useResidents';
import { useBookingsQuery, useCreateBookingMutation } from '@/shared/hooks/queries/useBookings';
import { usePermissions } from '@/context/AuthContext';
import type { Bed, BedStatus, Flat, Room } from '@/shared/types/api.types';

type ModalKind = 'flat' | 'room' | 'bed' | 'assign' | null;

interface FlatForm {
  name: string;
  address: string;
}

interface RoomForm {
  room_number: string;
}

interface BedForm {
  bed_label: string;
  rent_amount: number;
  status: BedStatus;
}

function computeRoomStats(roomId: string, beds: Bed[]) {
  const roomBeds = beds.filter((b) => b.room_id === roomId);
  return {
    totalBeds: roomBeds.length,
    occupiedBeds: roomBeds.filter((b) => b.status === 'occupied').length,
    vacantBeds: roomBeds.filter((b) => b.status === 'vacant').length,
  };
}

function computeFlatStats(flatId: string, rooms: Room[], beds: Bed[]) {
  const flatRooms = rooms.filter((r) => r.flat_id === flatId);
  const flatRoomIds = new Set(flatRooms.map((r) => r.id));
  const flatBeds = beds.filter((b) => flatRoomIds.has(b.room_id));
  return {
    totalRooms: flatRooms.length,
    totalBeds: flatBeds.length,
    occupiedBeds: flatBeds.filter((b) => b.status === 'occupied').length,
    vacantBeds: flatBeds.filter((b) => b.status === 'vacant').length,
  };
}

export function PropertiesPage() {
  const permissions = usePermissions();
  const flatsQuery = useFlatsQuery();
  const roomsQuery = useRoomsQuery();
  const bedsQuery = useBedsQuery();
  const residentsQuery = useResidentsQuery({ is_active: true });
  const bookingsQuery = useBookingsQuery({ status: 'active' });

  const createFlat = useCreateFlatMutation();
  const updateFlat = useUpdateFlatMutation();
  const createRoom = useCreateRoomMutation();
  const updateRoom = useUpdateRoomMutation();
  const createBed = useCreateBedMutation();
  const updateBed = useUpdateBedMutation();
  const createBooking = useCreateBookingMutation();

  const flats = flatsQuery.data?.items ?? [];
  const rooms = roomsQuery.data?.items ?? [];
  const beds = bedsQuery.data?.items ?? [];
  const residents = residentsQuery.data?.items ?? [];
  const activeBookings = bookingsQuery.data?.items ?? [];

  const loading = flatsQuery.isLoading || roomsQuery.isLoading || bedsQuery.isLoading;

  const [modal, setModal] = useState<ModalKind>(null);
  const [contextFlatId, setContextFlatId] = useState<string | null>(null);
  const [contextRoomId, setContextRoomId] = useState<string | null>(null);
  const [editingFlat, setEditingFlat] = useState<Flat | null>(null);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [editingBed, setEditingBed] = useState<Bed | null>(null);
  const [assignBed, setAssignBed] = useState<Bed | null>(null);
  const [error, setError] = useState<string | null>(null);

  const flatForm = useForm<FlatForm>();
  const roomForm = useForm<RoomForm>();
  const bedForm = useForm<BedForm>();
  const assignForm = useForm<{ resident_id: string; start_date: string }>();

  const roomsByFlat = useMemo(() => {
    const map = new Map<string, Room[]>();
    for (const flat of flats) map.set(flat.id, []);
    for (const room of rooms) {
      const list = map.get(room.flat_id) ?? [];
      list.push(room);
      map.set(room.flat_id, list);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.room_number.localeCompare(b.room_number, undefined, { numeric: true }));
    }
    return map;
  }, [flats, rooms]);

  const bedsByRoom = useMemo(() => {
    const map = new Map<string, Bed[]>();
    for (const bed of beds) {
      const list = map.get(bed.room_id) ?? [];
      list.push(bed);
      map.set(bed.room_id, list);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.bed_label.localeCompare(b.bed_label, undefined, { numeric: true }));
    }
    return map;
  }, [beds]);

  const bookedResidentIds = useMemo(
    () => new Set(activeBookings.map((b) => b.resident_id)),
    [activeBookings]
  );

  const bedOccupantMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const booking of activeBookings) {
      const resident = residents.find((r) => r.id === booking.resident_id);
      if (resident) map.set(booking.bed_id, resident.name);
    }
    return map;
  }, [activeBookings, residents]);

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

  const canManageFlats = permissions?.manage_flats;
  const canManageRooms = permissions?.manage_rooms;
  const canManageBeds = permissions?.manage_beds;

  const closeModal = () => {
    setModal(null);
    setEditingFlat(null);
    setEditingRoom(null);
    setEditingBed(null);
    setAssignBed(null);
    setContextFlatId(null);
    setContextRoomId(null);
    setError(null);
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
    roomForm.reset({ room_number: '' });
    setModal('room');
  };

  const openEditRoom = (room: Room) => {
    setContextFlatId(room.flat_id);
    setEditingRoom(room);
    roomForm.reset({ room_number: room.room_number });
    setModal('room');
  };

  const openAddBed = (flatId: string, room: Room) => {
    setContextFlatId(flatId);
    setContextRoomId(room.id);
    setEditingBed(null);
    const existing = bedsByRoom.get(room.id)?.length ?? 0;
    bedForm.reset({
      bed_label: `${room.room_number}-B${existing + 1}`,
      rent_amount: 8500,
      status: 'vacant',
    });
    setModal('bed');
  };

  const openEditBed = (bed: Bed) => {
    setContextFlatId(null);
    setContextRoomId(bed.room_id);
    setEditingBed(bed);
    bedForm.reset({
      bed_label: bed.bed_label,
      rent_amount: parseFloat(bed.rent_amount),
      status: bed.status,
    });
    setModal('bed');
  };

  const openAssign = (bed: Bed) => {
    setAssignBed(bed);
    assignForm.reset({
      resident_id: '',
      start_date: new Date().toISOString().slice(0, 10),
    });
    setModal('assign');
  };

  const onFlatSubmit = flatForm.handleSubmit(async (data) => {
    setError(null);
    try {
      if (editingFlat) {
        await updateFlat.mutateAsync({ id: editingFlat.id, payload: data });
      } else {
        await createFlat.mutateAsync(data);
      }
      closeModal();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const onRoomSubmit = roomForm.handleSubmit(async (data) => {
    const flatId = contextFlatId ?? editingRoom?.flat_id;
    if (!flatId) return;
    setError(null);
    try {
      if (editingRoom) {
        await updateRoom.mutateAsync({
          id: editingRoom.id,
          payload: { room_number: data.room_number },
        });
      } else {
        await createRoom.mutateAsync({ flat_id: flatId, room_number: data.room_number });
      }
      closeModal();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const onBedSubmit = bedForm.handleSubmit(async (data) => {
    const roomId = contextRoomId ?? editingBed?.room_id;
    if (!roomId) return;
    setError(null);
    try {
      if (editingBed) {
        await updateBed.mutateAsync({ id: editingBed.id, payload: data });
      } else {
        await createBed.mutateAsync({ room_id: roomId, ...data });
      }
      closeModal();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const onAssignSubmit = assignForm.handleSubmit(async ({ resident_id, start_date }) => {
    if (!assignBed) return;
    setError(null);
    try {
      await createBooking.mutateAsync({
        resident_id,
        bed_id: assignBed.id,
        start_date,
      });
      closeModal();
    } catch (err) {
      setError(getApiErrorMessage(err));
    }
  });

  const contextFlat = contextFlatId ? flats.find((f) => f.id === contextFlatId) : null;
  const contextRoom = contextRoomId ? rooms.find((r) => r.id === contextRoomId) : null;

  if (loading) {
    return (
      <Box>
        <PageHeader title="Properties" description="Manage your buildings, rooms, and beds" />
        <SkeletonLoader variant="stats" rows={4} />
        <Box sx={{ mt: 3 }}>
          <SkeletonLoader rows={3} />
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      <PageHeader
        title="Properties"
        description="Manage your buildings, rooms, and beds in one place"
        actions={
          canManageFlats ? (
            <Button variant="contained" startIcon={<AddIcon />} onClick={openAddFlat}>
              Add property
            </Button>
          ) : undefined
        }
      />

      {(flatsQuery.isError || roomsQuery.isError || bedsQuery.isError) && (
        <Alert severity="error">Could not load properties. Please try again.</Alert>
      )}

      <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { sm: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' } }}>
        {[
          { label: 'Properties', value: stats.properties },
          { label: 'Rooms', value: stats.rooms },
          { label: 'Total beds', value: stats.beds },
          { label: 'Vacant beds', value: stats.vacant, highlight: true },
        ].map((item) => (
          <Box
            key={item.label}
            sx={{
              p: 2,
              borderRadius: 2,
              border: 1,
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              {item.label}
            </Typography>
            <Typography
              variant="h5"
              fontWeight={700}
              color={item.highlight ? 'warning.main' : 'text.primary'}
            >
              {item.value}
            </Typography>
          </Box>
        ))}
      </Box>

      {flats.length === 0 ? (
        <EmptyState
          title="No properties yet"
          description="Start by adding a property (building). Then add rooms and beds inside it."
          icon={<HomeWorkOutlinedIcon sx={{ fontSize: 32 }} />}
          action={
            canManageFlats ? (
              <Button variant="contained" startIcon={<AddIcon />} onClick={openAddFlat}>
                Add your first property
              </Button>
            ) : undefined
          }
        />
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {flats.map((flat) => {
            const flatRooms = roomsByFlat.get(flat.id) ?? [];
            const flatRoomIds = new Set(flatRooms.map((r) => r.id));
            const flatBeds = beds.filter((b) => flatRoomIds.has(b.room_id));
            const liveStats = computeFlatStats(flat.id, rooms, beds);

            return (
              <Accordion
                key={flat.id}
                defaultExpanded
                disableGutters
                sx={{
                  borderRadius: '12px !important',
                  border: 1,
                  borderColor: 'divider',
                  overflow: 'hidden',
                  '&:before': { display: 'none' },
                }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ px: 2 }}>
                  <Box sx={{ display: 'flex', flex: 1, alignItems: 'center', gap: 1.5, minWidth: 0, pr: 1 }}>
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: 1.5,
                        bgcolor: 'action.selected',
                        color: 'primary.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <HomeWorkOutlinedIcon />
                    </Box>
                    <Box sx={{ minWidth: 0, flex: 1 }}>
                      <Typography fontWeight={700} noWrap>
                        {flat.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {flat.address}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {liveStats.totalRooms} rooms · {liveStats.totalBeds} beds · {liveStats.vacantBeds} vacant
                      </Typography>
                    </Box>
                    {canManageFlats && (
                      <Box sx={{ display: { xs: 'none', sm: 'flex' }, gap: 0.5 }} onClick={(e) => e.stopPropagation()}>
                        {canManageRooms && (
                          <Button size="small" startIcon={<AddIcon />} onClick={() => openAddRoom(flat.id)}>
                            Add room
                          </Button>
                        )}
                        <Button size="small" startIcon={<EditOutlinedIcon />} onClick={() => openEditFlat(flat)}>
                          Edit
                        </Button>
                      </Box>
                    )}
                  </Box>
                </AccordionSummary>

                <AccordionDetails sx={{ borderTop: 1, borderColor: 'divider', px: 2, pb: 2 }}>
                  {flatRooms.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
                      No rooms in this property yet.
                      {canManageRooms && (
                        <>
                          {' '}
                          <Button size="small" onClick={() => openAddRoom(flat.id)}>
                            Add a room
                          </Button>
                        </>
                      )}
                    </Typography>
                  ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                      {flatRooms.map((room) => {
                        const roomBeds = bedsByRoom.get(room.id) ?? [];
                        const roomStats = computeRoomStats(room.id, beds);

                        return (
                          <Box
                            key={room.id}
                            sx={{
                              p: 2,
                              borderRadius: 2,
                              border: 1,
                              borderColor: 'divider',
                              bgcolor: 'action.hover',
                            }}
                          >
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', gap: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <MeetingRoomOutlinedIcon color="primary" fontSize="small" />
                                <Box>
                                  <Typography fontWeight={600}>Room {room.room_number}</Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    {roomStats.totalBeds} beds · {roomStats.occupiedBeds} occupied · {roomStats.vacantBeds} vacant
                                  </Typography>
                                </Box>
                              </Box>
                              {canManageBeds && (
                                <Box sx={{ display: 'flex', gap: 0.5 }}>
                                  <Button size="small" startIcon={<AddIcon />} onClick={() => openAddBed(flat.id, room)}>
                                    Add bed
                                  </Button>
                                  {canManageRooms && (
                                    <Button size="small" onClick={() => openEditRoom(room)}>
                                      Edit
                                    </Button>
                                  )}
                                </Box>
                              )}
                            </Box>

                            {roomBeds.length === 0 ? (
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
                                No beds yet.
                                {canManageBeds && (
                                  <>
                                    {' '}
                                    <Button size="small" onClick={() => openAddBed(flat.id, room)}>
                                      Add a bed
                                    </Button>
                                  </>
                                )}
                              </Typography>
                            ) : (
                              <Box
                                sx={{
                                  mt: 1.5,
                                  display: 'grid',
                                  gap: 1,
                                  gridTemplateColumns: { sm: '1fr 1fr', lg: '1fr 1fr 1fr' },
                                }}
                              >
                                {roomBeds.map((bed) => (
                                  <Box
                                    key={bed.id}
                                    sx={{
                                      p: 1.5,
                                      borderRadius: 2,
                                      border: 1,
                                      borderColor: 'divider',
                                      bgcolor: 'background.paper',
                                    }}
                                  >
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1 }}>
                                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        <HotelOutlinedIcon fontSize="small" color="disabled" />
                                        <Typography fontWeight={500}>{bed.bed_label}</Typography>
                                      </Box>
                                      <StatusBadge status={bed.status} />
                                    </Box>
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                      {formatCurrency(bed.rent_amount)} / month
                                    </Typography>
                                    {bedOccupantMap.get(bed.id) && (
                                      <Typography variant="body2" fontWeight={500} sx={{ mt: 0.5 }}>
                                        {bedOccupantMap.get(bed.id)}
                                      </Typography>
                                    )}
                                    {canManageBeds && (
                                      <Box sx={{ mt: 1, display: 'flex', gap: 0.5 }}>
                                        <Button size="small" onClick={() => openEditBed(bed)}>
                                          Edit
                                        </Button>
                                        {bed.status === 'vacant' && (
                                          <Button
                                            size="small"
                                            startIcon={<PersonAddOutlinedIcon />}
                                            onClick={() => openAssign(bed)}
                                          >
                                            Assign
                                          </Button>
                                        )}
                                      </Box>
                                    )}
                                  </Box>
                                ))}
                              </Box>
                            )}
                          </Box>
                        );
                      })}
                    </Box>
                  )}

                  {flatBeds.length > 0 && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5, display: 'block' }}>
                      Est. revenue from occupied beds:{' '}
                      <Typography component="span" variant="caption" fontWeight={600}>
                        {formatCurrency(
                          flatBeds
                            .filter((b) => b.status === 'occupied')
                            .reduce((sum, b) => sum + parseFloat(b.rent_amount), 0)
                        )}
                      </Typography>
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
            );
          })}
        </Box>
      )}

      <ModalForm
        open={modal === 'flat'}
        title={editingFlat ? 'Edit property' : 'Add property'}
        onClose={closeModal}
        onSubmit={onFlatSubmit}
        submitLabel={editingFlat ? 'Update' : 'Create'}
        loading={createFlat.isPending || updateFlat.isPending}
      >
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField label="Property name" placeholder="e.g. Sunshine PG" fullWidth {...flatForm.register('name', { required: true })} />
          <TextField label="Address" placeholder="Full address" fullWidth multiline rows={2} {...flatForm.register('address', { required: true })} />
        </Box>
      </ModalForm>

      <ModalForm
        open={modal === 'room'}
        title={editingRoom ? 'Edit room' : 'Add room'}
        onClose={closeModal}
        onSubmit={onRoomSubmit}
        submitLabel={editingRoom ? 'Update' : 'Create'}
        loading={createRoom.isPending || updateRoom.isPending}
      >
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          {contextFlat && (
            <Alert severity="info">
              Inside: <strong>{contextFlat.name}</strong>
            </Alert>
          )}
          <TextField label="Room number" placeholder="e.g. 101" fullWidth {...roomForm.register('room_number', { required: true })} />
        </Box>
      </ModalForm>

      <ModalForm
        open={modal === 'bed'}
        title={editingBed ? 'Edit bed' : 'Add bed'}
        onClose={closeModal}
        onSubmit={onBedSubmit}
        submitLabel={editingBed ? 'Update' : 'Create'}
        loading={createBed.isPending || updateBed.isPending}
      >
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          {contextRoom && (
            <Alert severity="info">
              Room <strong>{contextRoom.room_number}</strong>
            </Alert>
          )}
          <TextField label="Bed label" placeholder="e.g. 101-B1" fullWidth {...bedForm.register('bed_label', { required: true })} />
          <TextField label="Monthly rent" type="number" fullWidth {...bedForm.register('rent_amount', { valueAsNumber: true })} />
          <TextField select label="Status" fullWidth defaultValue="vacant" {...bedForm.register('status')}>
            <MenuItem value="vacant">Vacant</MenuItem>
            <MenuItem value="occupied">Occupied</MenuItem>
            <MenuItem value="maintenance">Maintenance</MenuItem>
          </TextField>
        </Box>
      </ModalForm>

      <ModalForm
        open={modal === 'assign'}
        title="Assign resident to bed"
        onClose={closeModal}
        onSubmit={onAssignSubmit}
        submitLabel="Assign"
        loading={createBooking.isPending}
      >
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && <Alert severity="error">{error}</Alert>}
          {assignBed && (
            <Alert severity="info">
              Bed <strong>{assignBed.bed_label}</strong>
            </Alert>
          )}
          <TextField select label="Select resident" fullWidth {...assignForm.register('resident_id', { required: true })}>
            {residents
              .filter((r) => !bookedResidentIds.has(r.id))
              .map((r) => (
                <MenuItem key={r.id} value={r.id}>
                  {r.name}
                </MenuItem>
              ))}
          </TextField>
          <TextField
            label="Start date"
            type="date"
            fullWidth
            InputLabelProps={{ shrink: true }}
            {...assignForm.register('start_date', { required: true })}
          />
        </Box>
      </ModalForm>
    </Box>
  );
}
