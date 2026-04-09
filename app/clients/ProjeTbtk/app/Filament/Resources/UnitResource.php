<?php

namespace App\Filament\Resources;

use App\Filament\Resources\UnitResource\Pages;
use App\Models\Unit;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Illuminate\Validation\Rules\Unique;

class UnitResource extends Resource
{
    protected static ?string $model = Unit::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationLabel = 'Uniteler';
    protected static ?string $modelLabel = 'Unite';
    protected static ?string $pluralModelLabel = 'Uniteler';
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
                Forms\Components\TextInput::make('unit_no')
                    ->label('Unite No')
                    ->required()
                    ->numeric()
                    ->minValue(1)
                    ->unique(
                        ignoreRecord: true,
                        modifyRuleUsing: function (Unique $rule, Forms\Get $get): Unique {
                            return $rule
                                ->where('grade', (int) ($get('grade') ?? 0))
                                ->whereNull('deleted_at');
                        }
                    )
                    ->validationMessages([
                        'unique' => 'Bu sinifta ayni unite numarasi zaten var.',
                    ]),
                Forms\Components\TextInput::make('name')
                    ->label('Unite Adi')
                    ->required(),
                Forms\Components\Textarea::make('description')
                    ->label('Aciklama')
                    ->columnSpanFull(),
                Forms\Components\TextInput::make('order')
                    ->label('Liste Sirasi')
                    ->required()
                    ->numeric()
                    ->default(0),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('grade')
                    ->label('Sinif')
                    ->sortable(),
                Tables\Columns\TextColumn::make('unit_no')
                    ->label('Unite No')
                    ->sortable(),
                Tables\Columns\TextColumn::make('name')
                    ->label('Unite')
                    ->searchable(),
                Tables\Columns\TextColumn::make('order')
                    ->label('Sira')
                    ->numeric()
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->dateTime()
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\TrashedFilter::make(),
            ])
            ->actions([
                Tables\Actions\ViewAction::make(),
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\ForceDeleteBulkAction::make(),
                    Tables\Actions\RestoreBulkAction::make(),
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
            'index' => Pages\ListUnits::route('/'),
            'create' => Pages\CreateUnit::route('/create'),
            'view' => Pages\ViewUnit::route('/{record}'),
            'edit' => Pages\EditUnit::route('/{record}/edit'),
        ];
    }

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()
            ->withoutGlobalScopes([
                SoftDeletingScope::class,
            ]);
    }
}
