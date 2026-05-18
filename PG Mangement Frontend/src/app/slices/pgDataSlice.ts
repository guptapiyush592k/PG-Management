import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import {
  beds as initialBeds,
  flats as initialFlats,
  payments as initialPayments,
  rooms as initialRooms,
  tenants as initialTenants,
} from '@/mock-data';
import type { Bed, Flat, Payment, Room, Tenant } from '@/types';

interface PgDataState {
  flats: Flat[];
  rooms: Room[];
  beds: Bed[];
  tenants: Tenant[];
  payments: Payment[];
}

const initialState: PgDataState = {
  flats: initialFlats,
  rooms: initialRooms,
  beds: initialBeds,
  tenants: initialTenants,
  payments: initialPayments,
};

const pgDataSlice = createSlice({
  name: 'pgData',
  initialState,
  reducers: {
    setFlats: (state, action: PayloadAction<Flat[]>) => {
      state.flats = action.payload;
    },
    addFlat: (state, action: PayloadAction<Flat>) => {
      state.flats.push(action.payload);
    },
    updateFlat: (state, action: PayloadAction<Flat>) => {
      const i = state.flats.findIndex((f) => f.id === action.payload.id);
      if (i >= 0) state.flats[i] = action.payload;
    },
    setRooms: (state, action: PayloadAction<Room[]>) => {
      state.rooms = action.payload;
    },
    addRoom: (state, action: PayloadAction<Room>) => {
      state.rooms.push(action.payload);
    },
    updateRoom: (state, action: PayloadAction<Room>) => {
      const i = state.rooms.findIndex((r) => r.id === action.payload.id);
      if (i >= 0) state.rooms[i] = action.payload;
    },
    setBeds: (state, action: PayloadAction<Bed[]>) => {
      state.beds = action.payload;
    },
    addBed: (state, action: PayloadAction<Bed>) => {
      state.beds.push(action.payload);
    },
    updateBed: (state, action: PayloadAction<Bed>) => {
      const i = state.beds.findIndex((b) => b.id === action.payload.id);
      if (i >= 0) state.beds[i] = action.payload;
    },
    setTenants: (state, action: PayloadAction<Tenant[]>) => {
      state.tenants = action.payload;
    },
    addTenant: (state, action: PayloadAction<Tenant>) => {
      state.tenants.push(action.payload);
    },
    setPayments: (state, action: PayloadAction<Payment[]>) => {
      state.payments = action.payload;
    },
    addPayment: (state, action: PayloadAction<Payment>) => {
      state.payments.push(action.payload);
    },
  },
});

export const {
  setFlats,
  addFlat,
  updateFlat,
  setRooms,
  addRoom,
  updateRoom,
  setBeds,
  addBed,
  updateBed,
  setTenants,
  addTenant,
  setPayments,
  addPayment,
} = pgDataSlice.actions;

export const pgDataReducer = pgDataSlice.reducer;
