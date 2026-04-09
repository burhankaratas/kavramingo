<?php

namespace App\Filament\Resources;

use App\Filament\Resources\PlacementRuleResource\Pages;
use App\Models\PlacementRule;
use App\Models\Unit;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class PlacementRuleResource extends Resource
{
    protected static ?string $model = PlacementRule::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Yerlestirme Kurallari';
    protected static ?string $modelLabel = 'Yerlestirme Kurali';
    protected static ?string $pluralModelLabel = 'Yerlestirme Kurallari';
    protected static ?string $navigationGroup = 'Icerik';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('grade')
                    ->label('Sinif')
                    ->options([
                        9 => '9. Sinif',
                        10 => '10. Sinif',
                        11 => '11. Sinif',
                        12 => '12. Sinif',
                    ])
                    ->required(),
                Forms\Components\Select::make('unit_id')
                    ->label('Unite')
                    ->options(
                        Unit::query()
                            ->orderBy('grade')
                            ->orderBy('unit_no')
                            ->get()
                            ->mapWithKeys(fn (Unit $unit) => [
                                $unit->id => $unit->grade . '. Sinif / ' . $unit->unit_no . '. Unite - ' . $unit->name,
                            ])
                            ->all()
                    )
                    ->searchable()
                    ->required(),
                Forms\Components\TextInput::make('threshold_percent')
                    ->label('Tamamlama Esigi (%)')
                    ->required()
                    ->numeric()
                    ->minValue(1)
                    ->maxValue(100)
                    ->default(70),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('grade')
                    ->label('Sinif')
                    ->sortable(),
                Tables\Columns\TextColumn::make('unit.name')
                    ->label('Unite')
                    ->searchable(),
                Tables\Columns\TextColumn::make('threshold_percent')
                    ->label('Esik %')
                    ->sortable(),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListPlacementRules::route('/'),
            'create' => Pages\CreatePlacementRule::route('/create'),
            'view' => Pages\ViewPlacementRule::route('/{record}'),
            'edit' => Pages\EditPlacementRule::route('/{record}/edit'),
        ];
    }
}
