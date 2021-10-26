def input_analogs_code(filename, program_type, number_of_signals):
    if program_type == 3 and number_of_signals > 0:    # input analogs
        ai_file = open(filename, "a")
        ai_file.write('''(*//-------------------------------------------------------//*)
if fstCyc then 
   anaTotal  := ''' + str(number_of_signals) + '''; (* Количество входных аналоговых сигналов (114 модульных + 6 с тахометра + 9 расчётных) *)
   anaOffset := 10;  (* Смещение в таблице энергонезависимой памяти   *)
end_if;

(* ------- Инициализация всех настроек прописанных в программе ------- *)
if anaDefault THEN
  anaDefault := false;
  for i :=1 to anaTotal do
    analog[i].A_VAR_HA := 0.0;
    analog[i].A_VAR_HP := 0.0;
    analog[i].A_VAR_LP := 0.0;
    analog[i].A_VAR_LA := 0.0;
    analog[i].A_VAR_HI := 100.0;
    analog[i].A_VAR_LO := 0.0;
    analog[i].A_VAR_HT := 0.0;
    analog[i].A_VAR_LT := 0.0;
    analog[i].A_VAR_KS := 0.5;
    analog[i].A_VAR_SP := 20.0;
    analog[i].A_VAR_M  := 0.0;
    analog[i].A_CND    := A_INIT_MASK;
  end_for;
  ok := ppAnalogInit(); (*инициализация диапазонов датчиков и настроек коэффициентов датчиков*)
end_if;
(* RTN - Восстановление настроек из энергонезависимой памяти *)
if anaRead THEN
  anaRead := false;
  for i := 1 to anaTotal do (* регистры 11 -  802*)
    analog[i].A_VAR_HA := rtn_r32rd(ANY_TO_UINT(anaOffset+1  + (i-1)*12));
    analog[i].A_VAR_HP := rtn_r32rd(ANY_TO_UINT(anaOffset+2  + (i-1)*12));
    analog[i].A_VAR_LP := rtn_r32rd(ANY_TO_UINT(anaOffset+3  + (i-1)*12));
    analog[i].A_VAR_LA := rtn_r32rd(ANY_TO_UINT(anaOffset+4  + (i-1)*12));
    analog[i].A_VAR_HI := rtn_r32rd(ANY_TO_UINT(anaOffset+5  + (i-1)*12));
    analog[i].A_VAR_LO := rtn_r32rd(ANY_TO_UINT(anaOffset+6  + (i-1)*12));
    analog[i].A_VAR_HT := rtn_r32rd(ANY_TO_UINT(anaOffset+7  + (i-1)*12));
    analog[i].A_VAR_LT := rtn_r32rd(ANY_TO_UINT(anaOffset+8  + (i-1)*12));
    analog[i].A_VAR_KS := rtn_r32rd(ANY_TO_UINT(anaOffset+9  + (i-1)*12));
    analog[i].A_VAR_SP := rtn_r32rd(ANY_TO_UINT(anaOffset+10 + (i-1)*12));
    analog[i].A_VAR_M  := rtn_r32rd(ANY_TO_UINT(anaOffset+11 + (i-1)*12));
    analog[i].A_CND    := rtn_i32rd(ANY_TO_UINT(anaOffset+12 + (i-1)*12));
  end_for;
end_if;

(* --------------------- Изменение уставок с АРМ ---------------------- *)
IF flagCntCyc THEN 
  i := r32_to_i32(aniUstArr[1]);
  if (i > 0) and (i <= anaTotal) then
    analog[i].A_CND     := and_mask(analog[i].A_CND, not_mask(16#19100F0));
    analog[i].A_CND     := or_mask(r32_to_i32(aniUstArr[2]), analog[i].A_CND);
    analog[i].A_VAR_KS  := aniUstArr[3]; 
    analog[i].A_VAR_SP  := aniUstArr[4]; 
    analog[i].A_VAR_HA  := aniUstArr[5];
    analog[i].A_VAR_HP  := aniUstArr[6];
    analog[i].A_VAR_LP  := aniUstArr[7];
    analog[i].A_VAR_LA  := aniUstArr[8];
    analog[i].A_VAR_HI  := aniUstArr[9];
    analog[i].A_VAR_LO  := aniUstArr[10];
    (* В САУ ГПА ручной ввод и технологические уставки не используются *)                
    (* analog[i].A_VAR_M  :=aniUstArr[11];*)
    (* analog[i].A_VAR_HT :=aniUstArr[12];*)
    (* analog[i].A_VAR_LT :=aniUstArr[13];*)
  end_if;
end_if;
aniUstArr[1] := 0.0;

(* При загрузке контроллера снимаем "Ручной ввод" используемый при отладке *)
if fstCyc THEN
  for i := 1 to anaTotal do
    Analog[i].A_CND := set_bit(Analog[i].A_CND, 20, false);
  end_for;
end_if;   

(* Считываем коды АЦП с аналоговых модулей *)
if Alg.loc.Debug and not debug_old then
   for i := 1 to anaTotal - 0 do (* Не учитываем расчётные аналоги *)
      Analog[i].A_CND := set_bit(Analog[i].A_CND, 20, true);
   end_for;
elsif not Alg.loc.Debug then
   for i := 1 to anaTotal - 0 do
      Analog[i].A_CND := set_bit(Analog[i].A_CND, 20, false);
   end_for;
end_if;
debug_old := Alg.loc.Debug;

if alg.loc.Debug then (* режим имитации *)
   ok := ppAnalogImit();
else
   for i := 1 to anaTotal do
      analog[i].AI_VAR := F_AIN(i);
   end_for;
end_if;

(* Обработка расчётных и интерфейсных аналогов *)
ok := ppAnalogCalc();
  
(* Обработка аналогов *)
for i := 1 to anaTotal do
  FB_ANA_01(i, anaFlt[i], A_TRUST_DELAY); 
end_for;


(* Передача на верхний уровень уставки с состоянием *)
for i := 1 to anaTotal do
	anoVal[i].A_VAR := analog[i].A_VAR;
	anoVal[i].A_CND := analog[i].A_CND;
end_for;

(* Передача на верхний уровень настроек *)
if fstCyc then AnoUstStep := 10; end_if; (* Количество передаваемых аналогов на каждом цикле *)

AnoUstStart := AnoUstStop + 1;
AnoUstStop  := AnoUstStop + AnoUstStep;

for i := AnoUstStart to AnoUstStop do
   anoUst[i].A_VAR_AI :=analog[i].AI_VAR;  
   anoUst[i].A_VAR_KS :=analog[i].A_VAR_KS;
   anoUst[i].A_VAR_SP :=analog[i].A_VAR_SP;
   anoUst[i].A_VAR_HA :=analog[i].A_VAR_HA;
   anoUst[i].A_VAR_HP :=analog[i].A_VAR_HP;
   anoUst[i].A_VAR_LP :=analog[i].A_VAR_LP;
   anoUst[i].A_VAR_LA :=analog[i].A_VAR_LA;
   anoUst[i].A_VAR_HI :=analog[i].A_VAR_HI;
   anoUst[i].A_VAR_LO :=analog[i].A_VAR_LO;
   anoUst[i].A_VAR_M  :=analog[i].A_VAR_M; 
   anoUst[i].A_VAR_D  :=analog[i].A_VAR_D; 
   anoUst[i].A_VAR_HT :=analog[i].A_VAR_HT;
   anoUst[i].A_VAR_LT :=analog[i].A_VAR_LT;
   
   if i >= anaTotal then AnoUstStop := 0; exit; end_if;
end_for;


(* RTN - запись *)
(* регистры 11 - 802 *)
iAnoRtn := iAnoRtn + 1;
if iAnoRtn < 1 or iAnoRtn > anaTotal then iAnoRtn := 1; end_if;

anaOffsetTmp := ANY_TO_UINT(anaOffset  + (iAnoRtn - 1) * 12);
rtnOk := rtn_r32wr(anaOffsetTmp +  1, analog[iAnoRtn].A_VAR_HA);
rtnOk := rtn_r32wr(anaOffsetTmp +  2, analog[iAnoRtn].A_VAR_HP);
rtnOk := rtn_r32wr(anaOffsetTmp +  3, analog[iAnoRtn].A_VAR_LP);
rtnOk := rtn_r32wr(anaOffsetTmp +  4, analog[iAnoRtn].A_VAR_LA);
rtnOk := rtn_r32wr(anaOffsetTmp +  5, analog[iAnoRtn].A_VAR_HI);
rtnOk := rtn_r32wr(anaOffsetTmp +  6, analog[iAnoRtn].A_VAR_LO);
rtnOk := rtn_r32wr(anaOffsetTmp +  7, analog[iAnoRtn].A_VAR_HT);
rtnOk := rtn_r32wr(anaOffsetTmp +  8, analog[iAnoRtn].A_VAR_LT);
rtnOk := rtn_r32wr(anaOffsetTmp +  9, analog[iAnoRtn].A_VAR_KS);
rtnOk := rtn_r32wr(anaOffsetTmp + 10, analog[iAnoRtn].A_VAR_SP);
rtnOk := rtn_r32wr(anaOffsetTmp + 11, analog[iAnoRtn].A_VAR_M );
rtnOk := rtn_i32wr(anaOffsetTmp + 12, and_mask(analog[iAnoRtn].A_CND, A_SAVE_MASK));
''')
        ai_file.close()
        print(f'{number_of_signals} Analogs done!')
    else:
        print('There are no input analog signals in your file.')


def input_analogs_init_code(number_of_signals, signal_names):
    if number_of_signals > 0:
        ainit_file = open('ppAnalogInit.stf', "w")
        ainit_file.write('''
(* Файл формируется со значениями "по умолчанию", требующих даленйшей корректировки!!! *)        
(* Уставки HP и LP по умолчанию отключены *)
    
        (*      №,\tOFF,\tHI,\t\tLO,\t\tHP,\t\tLP,\t\tKS,\t\tSP,\t\tTYPE *)\n''')
        for idx in range(1, number_of_signals + 1):
            if 'Температура' in signal_names[idx - 1]:
                scale_max = 200.0
                scale_min = -50.0
                hi_prealarm = 200.0
                lo_prealarm = -50.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 2
            elif 'Перепад' in signal_names[idx - 1]:
                scale_max = 100.0
                scale_min = 0.0
                hi_prealarm = 100.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1
            elif 'Давление' or 'Разрежение' in signal_names[idx - 1]:
                scale_max = 1000.0
                scale_min = 0.0
                hi_prealarm = 1000.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1
            elif 'Уровень' in signal_names[idx - 1]:
                scale_max = 100.0
                scale_min = 0.0
                hi_prealarm = 100.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1
            elif 'Напряжение' in signal_names[idx - 1]:
                scale_max = 300.0
                scale_min = 0.0
                hi_prealarm = 300.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 4
            elif 'Положение' in signal_names[idx - 1]:
                scale_max = 100.0
                scale_min = 0.0
                hi_prealarm = 100.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1
            elif 'Загазованность' in signal_names[idx - 1]:
                scale_max = 100.0
                scale_min = 0.0
                hi_prealarm = 100.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1
            else:
                scale_max = 100.0
                scale_min = 0.0
                hi_prealarm = 100.0
                lo_prealarm = 0.0
                smothing_koef = 0.5
                speed_koef = 20.0
                signal_type = 1

            ainit_file.write(f'ok := fAinit(\t{idx},\tD_ON,\t{scale_max},\t{scale_min},\t{hi_prealarm},\t{lo_prealarm},'
                             f'\t{smothing_koef},\t{speed_koef},\t{signal_type}); \t\t\t(* {idx}\t{signal_names[idx - 1]} \t\t\t\\\\\t\t\t*)\n')
        ainit_file.write('\n\nppAnalogInit := 0;')
        ainit_file.close()
    else:
        print('Number of analogs in equal of less than 0!')


def input_discrete_code(filename, number_of_signals, signal_names):
    if number_of_signals > 0:  # input discrets
        # pDiscrets code
        di_file = open(filename, "a")
        di_file.write('''
if fstCyc then
disTotal  := ''' + str(number_of_signals) + '''; (* Количество входных дискретных сигналов *)''')
        for idx in range(1, number_of_signals + 1):
            di_file.write('''
(* ''' + str(idx) + '''\t''' + signal_names[idx - 1] + '''                                                               //    *)
disIn[''' + str(idx) + '''].T_off := any_to_dint(t#100ms);
disIn[''' + str(idx) + '''].T_on  := any_to_dint(t#100ms);
disIn[''' + str(idx) + '''].N_Invert :=false;
''')
        di_file.write('''
end_if;
(* Обработка дискретов *)
(* Если включен режим отладки, то выполняем имитацию входных дискретов *)
if Alg.loc.debug then 
	ok := ppDiscrImit();
	(* Обработка дискретного сигнала *)
	for i:= 1 to disTotal  do
		if  disIn[i].N_Invert then
			disIn[i].NOut := not disIn[i].Val;
		else
			disIn[i].NOut := disIn[i].Val;
		end_if;
	end_for;
(* Иначе, считываем входные дискретные сигналы с входных каналов *)	
else 
	for i := 1 to disTotal do
	   disIn[i].Val_in := F_DIN(i);
	   FBDis(i);
	end_for;
end_if;

(*Передача данных на АРМ входных переменных*)
(*Передача данных на АРМ*)
for i := 1 to 13 do
   dnoVal[i] := 0;
   for j := 0 to 31 do
      dnoVal[i] := or_mask(dnoVal[i], shl(ANY_TO_DINT(disIn[(i-1)*32+j+1].NOut), j));
   end_for;
end_for;
''')
        print('Input Discrets done!')
    else:
        print('There are no input discrete signals in your file.')



